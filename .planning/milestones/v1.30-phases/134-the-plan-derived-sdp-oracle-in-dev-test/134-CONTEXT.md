# Phase 134: The Plan-Derived SDP Oracle in `dev test` - Context

**Gathered:** 2026-08-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Teach `derive_plan` to emit the SDP leg from `sdp_capability()`, implement its **read-back-equality**
oracle behind a no-default truth table, render the leg's honesty surface (`HELD`/`NOT-HELD`/`NOT-RUN`,
the N-of-M change, the "rewrite" recovery wording), and triage gh#20 against the new baseline gate.

**In scope:** four new op strings (`write-baseline-b`, `write-baseline-a`, `write-inhibited`,
`write-restored`) joining Phase 133's `sdp-lock`/`sdp-unlock`; `derive_plan` emitting the leg for the 43
ALLOW chips and NA-carrying steps for the 41 REFUSE chips; the oracle's truth table and its degenerate
arms; a run-time baseline gate that refuses to lock a chip whose write path did not transition; the
`HELD`/`NOT-HELD`/`NOTRUN` report field + `to_dict()` key + `SCHEMA_VERSION` 1.2→1.3; the two-form
recovery line and its scoped "rewrite"-not-"erase" pytest; the `_ALWAYS_WRITES_NOTICE` rewrite and its
derived-count test; the exit-precedence fix; the six laundering-route tests; the gh#20 triage finding.

**Out of scope — and load-bearing:**
- **No new command-line option.** `dev test` keeps zero options (LEG-01's constraint).
- **`firestarter` (firmware) is not touched at all.** Host-only, no lockstep, no `.hex` re-cut.
- **`eprom_operations.py` stays ring-fenced** (`FUT-MYPY-02`, operator decision 2026-08-03). Call
  `sdp_lock` (`:1784`), `sdp_unlock` (`:1736`), `write_eprom` (`:1583`), `read_eprom` (`:650`) — never
  type-fix, and per **D-01** never edit it to surface the `0x86` ack.
- **No `write --sdp-relock`.** Backlog 999.28; the `write` handler is not touched.
- **No dev-tools channel gating.** Phase 136 (CHAN-\*).
- **No claim gate, no honesty ledger, no release notes, no gh#12 reply.** Phase 137 (CLOSE-\*). Per
  **D-16**, the gh#20 *public reply* is Phase 137's too — this phase records the finding only.
- **No `tools/check_*.py` string-literal scanner.** That is Phase 137's CLOSE-03 (**D-13**).
- **No watermark edit.** The `35` in `pyproject.toml` is not touched; this phase spends against it.
- **No new verdict status.** Research §2.1 measured a sixth status as an anti-feature —
  `_verdict_code` is `.get(verdict, 0)`, so an unrecognised verdict exits **0**, and it would miss every
  `build_db_diff` arm. Use the existing five.

</domain>

<decisions>
## Implementation Decisions

### Four measured corrections — read before planning

Each was measured live this session against the milestone branch, not inherited from the record.

1. **The `0x86` opt-out ack is UNOBSERVABLE from `chip_test.py`.** `_disconnect_programmer()` sets
   `self.comm = None` (`eprom_operations.py:414-416`) and `_operation_context`'s `finally` calls it after
   every operator call, so `comm.seen_message_ids` is gone by the time `write_eprom` returns. The ack is
   already folded into the bool at `:1654-1662`. **Research's truth-table branch 5 ("the ack readable as
   a *separate* signal") is not implementable as written** — D-01 replaces it.

2. **Criterion 1's / LEG-01's / LEG-02's "four-step leg" is measured-wrong; the leg is SIX steps.** See
   D-06. Both readings must appear in the phase record (the 133-RECORD §4 precedent).

3. **`dev test`'s exit precedence is inverted against its own documentation.** `_VERDICT_EXIT_CODES`
   maps `marginal → 2`, `BAD → 1` (`cli_handlers.py:1888-1894`) and the code is
   `max(_verdict_code(r.verdict) for r in results)` — so `max(1, 2) = 2` and **marginal beats BAD**. The
   source comment at `:1888-1890` says *"BAD beats marginal via `max`"* and `dev_test`'s docstring says
   *"2 if any step is marginal (and none BAD), 1 if any step is BAD"*. Both are false today. D-14 fixes
   it, because LEG-06 and criterion 2 both require the leaked-lock case to exit **1** and the truth table
   has three `marginal` arms.

4. **133 D-15's "file budget is spent — 0 slots for Phase 134" is inverted and must not be inherited.**
   `MIN_CHECKED_SOURCE_FILES = 120` is a **floor** (`checked < 120` ⇒ fail, `check_mypy_watermark.py:48`
   and its docstring at `:21-23`). Adding source files *raises* `checked` (now **124**) and moves further
   **above** the floor; the margin protects against coverage *loss*, not against additions. **Phase 134
   is free to add test modules.** The real budget is the **mypy headroom: 2 errors (33 vs watermark 35)**
   — and note `cli_handlers.py` IS in the mypy strict island (`disallow_untyped_defs = true`,
   `check_untyped_defs = true`), while `chip_test.py` and `diagnostic_report.py` are in neither.

### The oracle's verdict axis

- **D-01:** **`write_eprom`'s bool is a PRECONDITION signal, never the verdict.** On a `0x0D` write with
  `FLAG_SKIP_SDP_UNLOCK` set, `True` is reachable only when the state machine succeeded **and** the
  `0x86` ack was observed (`eprom_operations.py:1654-1662` forces `is_ok = False` otherwise) — so `True`
  proves the experiment ran as designed. `False` ⇒ **marginal, never BAD**, with a `reason` naming both
  candidate causes (ack not honoured / transport fault) and the firmware-update instruction. The
  read-back alone decides OK vs BAD. Rejected: adding a narrow read-only ack seam to `EpromOperator`
  (would disambiguate ack-missing from transport-failed, but it is a behavioural edit inside the
  ring-fenced `eprom_operations.py`, which this milestone has not been asked to reopen); and read-back
  only, ignoring the bool (purest LEG-05 reading, but on firmware that silently auto-unlocked the
  read-back equals B and the leg reports BAD — accusing the chip of leaking when the host's own flag was
  ignored).

- **D-02:** **`write_eprom` returned `False` and the read-back equals B ⇒ `marginal`, not BAD.** The most
  likely cause is the opt-out not being honoured — firmware auto-unlocked, then wrote B successfully — so
  BAD would over-attribute a host-side cause to the chip. Rejected: BAD (a full change to B is a hard
  fact and louder, but manufactures a chip-fault report for a community member on older firmware); and a
  split where fully-B is marginal but a *partial* change is BAD (most discriminating and defensible, but
  costs an extra truth-table arm and fixture, and D-01 already routes every failed-precondition case to
  one place).

- **D-03:** **The polarity proof is the full 2×2 cross product:** `(True, A) ⇒ OK` · `(True, B) ⇒ BAD` ·
  `(False, A) ⇒ marginal` · `(False, B) ⇒ marginal`. The first two hold the bool **constant** and vary
  only the read-back — a strictly stronger proof than research's, because a bool-driven implementation
  cannot yield two different verdicts from one identical bool. The last two pin the precondition gate in
  both read-back directions. **Record P-03 prevention 4's `(False, A) ⇒ OK` as overturned by correction
  1**, with the reason; do not implement it. Rejected: three legs, dropping `(False, B)` (leaner, but the
  polarity pin then does not itself show suppression in both directions); and following P-03 literally
  (contradicts D-01 and D-02).

- **D-04:** **Degenerate read-backs split by cause: LENGTH ⇒ BAD, CONTENT ⇒ marginal.** An empty or
  wrong-length read-back is BAD (exit 1) — the oracle had no input, per P-02's explicit *"`VERDICT_BAD`,
  never `SKIPPED`"*. A correct-length but degenerate *content* read-back (all-`0xFF` / all-`0x00`) routes
  through `classify_fingerprint` and lands **marginal** on `blank/contact` or `transport`, so a loose
  socket reads as a contact fault rather than a chip finding. LEG-08 permits either; this is the split.
  Rejected: all four arms BAD (loudest, and keeps `_FF_RATIO_THRESHOLD`'s tunable number out of the
  oracle entirely — but files a bad socket as a chip fault); and all four marginal (cleanest semantics,
  but makes an empty read-back non-blocking, the shape P-02 warns reads as passing).

- **D-05:** **The non-laundering obligation is a TEST, not an argument** (research §2.2 branch 3a).
  Because D-04 routes content-degeneracy through `classify_fingerprint`, a fully-B read-back must be
  provably unable to reclassify as `blank/contact`. Measured: `B = ~A`, and over a 256-byte region `A`
  contains ~1 zero byte, so `B`'s `ff_ratio ≈ 0.004` against `_FF_RATIO_THRESHOLD = 0.98`
  (`chip_test.py:127`). Assert it against the live generators for the real region, not a literal.

### The leg's composition and the baseline gate

- **D-06:** **SIX steps, and criterion 1's "four" is corrected in the record:**
  `write-baseline-b` · `write-baseline-a` · `sdp-lock` · `write-inhibited` · `sdp-unlock` ·
  `write-restored`. The count assertion **and** the REFUSE-chip NA test both pin **six**. Why the
  inherited "four" is wrong: it was written before LEG-04 mandated two transition directions, and the
  ROADMAP's own enumeration omits `write-restored` — which is the only step producing evidence the part
  was left writable, on a family whose protection state cannot be read back. Research §3.1's happy-path
  wording (*"the unlock sequence was emitted **and the part accepted a write afterwards**"*) is
  unsupportable without it. Rejected: five steps dropping `write-restored` (closest to the ROADMAP's
  enumeration, but the run then ends on `sdp-unlock OK` — an emission claim — so LEG-12's `NOT-HELD` has
  no evidence behind it); and exactly four via one folded `sdp-baseline` op and no `write-restored` (needs
  no correction to the criterion, but pays both costs).

- **D-07:** **Two baseline ops, not one.** `write-baseline-b` and `write-baseline-a`, each folding write +
  read-back verification into its own single-run arm. Measured reason: `DiagnosticReport.render()`'s
  console table shows only `op`, `verdict`, `error_code`, `fingerprint` — **`reason` appears only in the
  markdown table and the JSON block**, so detail hidden in `reason` is invisible to whoever reads the
  terminal, and this is the step that decides whether a lock is emitted at all. Two ops make the failing
  direction legible in the op string itself — the `write-partial` precedent (`chip_test.py:282-288`:
  *"every consumer that reads `StepResult.op` sees it without learning a new field"*). Rejected: one
  folded `sdp-baseline` op (smallest vocabulary growth, but console-invisible); and reusing the shipped
  `write`/`verify` for the A direction with one new B op (fewest new ops, but the leg stops being a
  contiguous appended block and the A direction's verdict comes from `verify_eprom`'s bool via
  `_dispatch_multi_run` — the boolean-oracle path P-03 exists to keep the leg out of).

  **Why reuse cannot satisfy LEG-16, stated for the record:** research §1.1's *"step 1 should NOT get a
  new op — reuse the existing `write` + `verify`"* fails LEG-16's own fixture. The shipped pair writes A
  only; on a chip already holding A from an earlier run with a dead write path, `verify_eprom` returns
  `True` and the step reports OK. **The B direction is what makes the gate real** — a no-op write leaves
  A in place, so verify-B fails and the step goes BAD.

- **D-08:** **A dedicated baseline gate: `_baseline_closes_sdp_gate` in `run_plan`, mirroring
  `_id_step_closes_gate`'s existing shape** (`chip_test.py:974`), keyed on a new `_SDP_LEG_OPS` set, with
  its **own** reason string. It closes on **any** baseline verdict that is not OK — BAD, marginal,
  SKIPPED, NA — because a contact fault is as disqualifying as a dead write path. Closes `sdp-lock`,
  `write-inhibited` and `write-restored`; `sdp-unlock` is never attempted because nothing was locked.
  **No change to Phase 133's frozen `_dispatch_sdp(op, name, eprom_data, operator)` signature.**
  Rejected: reusing the existing `destructive_gate_closed` flag (zero new machinery, already covered by
  133's proofs — but the SKIPPED steps would render `_DESTRUCTIVE_GATE_REASON`'s chip-ID wording, telling
  a reader the chip ID closed the gate when the write path did); and a precondition check inside the lock
  arm (keeps the logic next to the decision, but reopens the signature 133 D-01 deliberately pinned as a
  forward contract).

  **This is a SEVENTH route to a non-running oracle**, on top of research's R1–R6. Under D-08 + D-15 it
  fails closed (exit 1 from the baseline BAD, or ≥2 via the NOT-RUN floor), so it is not a laundering
  route — but it must be tested in the same family and named as the seventh in the record.

  ⚠ **D-08's clause *"`sdp-unlock` is never attempted because nothing was locked"* is MEASURED-WRONG and
  is superseded by D-20.** `OP_SDP_UNLOCK` is deliberately absent from `_DESTRUCTIVE_OPS` (LEG-09,
  `chip_test.py:663`), so as D-08 is literally written the unlock step would RUN. Record both readings.

- **D-20:** **`sdp-unlock` joins the baseline-gate set and renders SKIPPED when that gate closed.**
  Operator decision 2026-08-04, resolving research §4.1's OQ-1. Its reason names *"no lock was emitted —
  baseline gate closed"*, never `_DESTRUCTIVE_GATE_REASON`'s chip-ID wording. Without this, a
  dead-write-path run (gh#20's exact shape) ends on `sdp-unlock OK` — an emission claim on a step whose
  premise did not hold, the P-06 shape, and the report's last word would be a success claim about a part
  that was never locked, on a family whose protection state cannot be read back. **This does NOT violate
  LEG-09:** LEG-09 is scoped to the ***destructive*** gate (`_DESTRUCTIVE_OPS` membership +
  `test_unlock_exempt_from_destructive`), a structurally different mechanism from the new baseline gate;
  state that distinction in the record and pin it with a test asserting a *destructive*-gate closure
  still never skips the unlock, so Phase 133's LEG-09 proof stays byte-identically green. Measured
  consequence for gh#20's shape: `write-baseline-b` BAD → gate closes → five SKIPPED ⇒ N=5, M=10 ⇒ the
  banner reads **"5 of 10 ran"** instead of today's misleading "4 of 4". Rejected: following D-08
  literally and letting the unlock run (no amendment to a locked decision and LEG-09's proof untouched by
  construction, but it ships the false OK described above); and running the unlock while forcing a
  non-OK verdict (keeps the emission as defence-in-depth if the gate itself is ever wrong, but creates a
  second place where a verdict stops following from the step's own outcome — D-15 is already one).

- **D-09:** **`_ALWAYS_WRITES_NOTICE` stays one static notice printed first; its number is pinned by a
  DERIVED test.** Measured constraint: the notice is printed first, unconditionally, before the SAFE-04
  absent-chip hard-fail and before `write_scope` resolution or `derive_plan` (D-04's deliberate ordering,
  pinned by `test_always_writes_notice_is_the_first_line_unconditionally`), so it cannot contain a
  per-chip derived count. Rewrite the prose to name the SDP lock, to state the part is left unlocked on a
  **completed** run, and to give the aborted-run recovery in the word **"rewrite"**; then add a test that
  **derives** the plan for a representative ALLOW chip, computes the write-pass count, and asserts the
  notice's number equals it (P-08 prevention 2 — derive it, do not write the number twice). Measured
  today: an ALLOW chip takes **6 write passes** over its 256-byte region (A×2 from the shipped write step
  at `runs=2`, then B, A, B, A) against a notice promising "written twice". Rejected: a two-part notice
  with a per-chip second line after `derive_plan` (verified safe on ordering — nothing energises until
  `read_hardware_revision_value` at `cli_handlers.py:2147`, and ALLOW chips are never UV so no consent
  prompt precedes it — but it adds a second output surface to keep true); and interpolating the count
  into the first line (breaks D-04's printed-FIRST guarantee and its committed test).

### The report surface

- **D-10:** **A named three-valued STRING field on `DiagnosticReport`, emitted in `to_dict()`, with
  `SCHEMA_VERSION` 1.2 → 1.3.** LEG-12 requires the field in **both** surfaces, which overrides research
  §3.2's *"No new `to_dict()` field"*. The bump uses the same additive argument as 1.1 → 1.2
  (`diagnostic_report.py:55`). **Never a boolean** — P-06 prevention 3: a JSON `true` on a key like
  `locked` or `protection_enabled` is read as ground truth for a state this family cannot report, so a
  committed test must assert no such boolean exists anywhere in `to_dict()`. Verified tolerant:
  `tools/parse_devtest_issue.py` accepts `schema_version` by presence only (research §1.3). Rejected:
  deriving the value at render time with no field (research's discipline intact, no bump — but if the SDP
  steps are absent entirely, laundering route R6, there is nothing to derive from and the field renders
  nothing, which is the exact invisibility LEG-12 closes); and field + JSON with no bump (smallest diff,
  but the artifact shape changes while its own version claims it did not, in the milestone whose close
  phase arms a claim gate over that kind of statement).

- **D-11:** **The `dedup_fingerprint` reset for all 43 ALLOW chips is ACCEPTED and RECORDED as a cost.**
  `dedup_fingerprint` hashes `op=verdict:cls` per step (`diagnostic_report.py:183`), so six new steps
  necessarily re-key every ALLOW chip: b14/b15-era reports stop grouping with v1.30-era ones and their
  accumulated N≥2 promotion counts reset. **Name gh#20's orphaned `00e121446ceb` explicitly inside the
  LEG-18 finding** and hand the cost to Phase 137's release notes. Same mechanism v1.21 D-08 relied on to
  keep partial and full runs apart — here a cost, not a feature. Rejected: excluding SDP steps from the
  hash (preserves continuity and the promotion ladder, but two reports differing *only* in their SDP
  outcome would dedup as identical — a leaked lock grouping with a held one, blinding the mechanism that
  decides which reports get triaged); and carrying a second legacy fingerprint (preserves continuity
  without blinding dedup, but adds a field and a hash nothing else needs).

- **D-12:** **Two recovery forms, and a line prints on the happy path.** Loud form when the lock was
  emitted and the run did not confirm the part writable again; **neutral** one-liner on the happy path
  affirming the part was left unlocked and that this is evidence, not a guarantee, on a family whose
  state is unreadable. Via `click.echo`, matching `_ALWAYS_WRITES_NOTICE`'s precedent so it reaches
  console/`CliRunner` capture regardless of log-level wiring. Research §3.2's own position: an
  unconditional warning trains dismissal and would spend the signal on the case it exists for, but
  silence is not a statement. Rejected: loud-only with silence on success (max signal, but the report
  never affirms the end state and the `HELD` field becomes the only place to find it); and one
  always-loud line (one string to keep honest, but it is the shape users learn to skim).

  **Honest residual, inherited from 133 D-07 and NOT closed here:** after a Ctrl-C mid-leg,
  `results = run_plan(...)` (`cli_handlers.py:2161`) never completes, so **neither form prints and there
  is no report at all**. The mitigation is D-09's rewritten notice, printed up front where it is
  guaranteed to be seen — not a `finally` handler. Do not claim otherwise (research §3.2's caveat).

- **D-13:** **LEG-14's gate is a SCOPED pytest, not a whole-report grep, and it hands off to CLOSE-03.**
  Hoist the SDP recovery wording into named module-level string constants and scan **those constants
  only**: "rewrite" present, "erase" absent, plus a non-vacuity leg proving the gate fails on a planted
  constant saying "erase". Runs in CI via pytest. **Measured trap that rules out the literal reading:**
  the report legitimately contains "erase" — `derive_plan`'s NA reason (*"protocol 0x0D (28C family) has
  no erase operation; each page write auto-erases internally"*, `chip_test.py:577-580`) reaches the
  markdown table and JSON, and `_ALWAYS_WRITES_NOTICE` says "write/verify/erase step". A whole-report
  grep goes RED on correct text and would need exemptions on day one — the 133 D-14 `_sample` shape.
  Record a note handing Phase 137's CLOSE-03 the constant names so it **extends** rather than duplicates.
  Rejected: authoring 137's `tools/check_*.py` scanner now (front-loads the mechanism and puts it where
  CI runs tools, but builds another phase's requirement inside this one — in a project whose executors
  have ticked multi-plan requirements prematurely 4× — and CLOSE-02's target-resolution legs would then
  be authored against a tool that already exists).

### Exit codes and the N-of-M banner

- **D-14:** **Fix the exit precedence so BAD outranks marginal.** Replace the naive `max` with explicit
  precedence, **restoring the behaviour the source comment and the `dev_test` docstring already claim**
  rather than changing a designed contract (correction 3). Pin a mixed BAD+marginal run at exit **1**,
  with a non-vacuity leg. **Audit every existing test asserting exit 2 on a mixed run** before changing
  it, and put the correction in the record with both readings; Phase 137's ledger should carry it.
  Rejected: leaving it and scoping LEG-06's test to a marginal-free run (zero blast radius, but the
  milestone's headline finding can then arrive wearing the inconclusive code, and criterion 2's "exit
  code 1" is satisfied only conditionally); and correcting only the two prose claims to match the code
  (smallest honest move, but LEG-06 and criterion 2 would need a requirement-text amendment saying the
  leg's most important finding cannot produce exit 1).

- **D-15:** **A NOT-RUN oracle on an ALLOW chip keeps verdict `SKIPPED` and gets an exit FLOOR of 2.**
  The step stays `SKIPPED` so it stays out of `_RAN_VERDICTS` and `N < M` — the ratio drops as LEG-13
  requires — and `dev_test`'s exit computation gains **one** non-verdict term: if the chip is ALLOW and
  the field reads `NOT-RUN`, the exit is at least 2. **Why not `marginal`:** `_RAN_VERDICTS = frozenset({
  OK, BAD, MARGINAL})` (`chip_test.py:1500`), so `marginal` counts as *ran* — recording a non-running
  oracle as marginal would hold `N == M` and defeat LEG-13 outright. Stated cost: the exit code stops
  being a pure function of step verdicts; pin it with a test. Rejected: marginal plus narrowing
  `_RAN_VERDICTS`/`count_applicable` (keeps the exit pure, but edits a shipped counting rule shared by
  every op to accommodate one step, and 133's parity gate carries an exemption row pointing at it); and
  `SKIPPED` at exit 0 relying on the field alone (no exit-map change, and LEG-12's own wording
  anticipates it — but `firestarter dev test at28c256` returns 0 and a reporter files it as PASS, the
  P-04 shape).

  **Measured, and it narrows LEG-13's work:** for an ALLOW chip the SDP steps carry `supported=True`, so
  `count_applicable`'s `M = sum(1 for s in plan.steps if s.supported) + len(plan.locked_destructive)`
  already includes them, and a `SKIPPED` result is already excluded from `N`. **The ratio already drops —
  LEG-13 needs a pinning test, not new counting logic.** The REFUSE case (`supported=False` ⇒ excluded
  from both M and N ⇒ `N == M`) is out of LEG-13's scope, which says "for ALLOW chips"; record that
  reading explicitly rather than silently extending it.

- **D-16:** **gh#20's finding is recorded in THIS phase; the public reply is Phase 137's.** LEG-18's text
  says the finding is *"recorded"*, not posted. Record: gh#20 is the dead-write-path case (AT28C256, host
  `3.0.0b14`, Rev 2.3, `blank-check`/`write`/`verify` all BAD, fingerprint `indeterminate`, banner
  `4 of 4`, VPP 11.8 V / VPE 13.7 V), D-08's gate would refuse to lock it, and D-11 orphans its
  `00e121446ceb`. **File the underlying AT28C256 write failure as a backlog item with a named owner** so
  it does not become another unowned acknowledgement. The reply goes to Phase 137 behind the blocking
  operator wording-review gate CLOSE-06 already has, so all outward-facing wording clears one review at
  close. Rejected: commenting in this phase behind its own operator gate (answers the reporter while
  context is fresh, but makes an outward-facing claim about an unclosed milestone before the claim gate
  policing that wording is armed); and record-only with no reply ever planned (smallest surface, but a
  community member who filed a real report gets no response and nothing schedules one).

- **D-17:** **All six laundering routes R1–R6 are tested; R1/R2 use a synthetic NONZERO chip-id and are
  labelled unreachable.** Research measured the chip-ID destructive gate structurally vacuous for the
  entire SDP population: **all 43 ALLOW chips have `chip-id == 0`**, so `derive_plan` emits
  `Step(op=OP_ID, supported=False, reason="no chip-id in DB entry")` and an NA id step does not close the
  gate (`_id_step_closes_gate`). Drive R1/R2 through a synthetic DB entry with a nonzero chip-id so the
  full causal chain — id step → mismatch → gate closes → `sdp_lock` not called → `NOT-RUN` rendered — is
  genuinely exercised, then label them **in-source and in the record** as unreachable in production
  today, correct if a chip-id is ever added, defence-in-depth and never live protection. **Requirements
  and report text must not claim "the leg is gated by chip ID"** — research §2.6 flags that as a v1.22
  C-5 class overclaim, and it makes D-12's recovery line *more* load-bearing, not less. Rejected: forcing
  the gate flag directly (simpler, but proves the gate, not the route — the id-step→gate causation goes
  untested); and testing four and recording R1/R2 unreachable (most literal about the ceiling, but
  LEG-17 says six and would be ticked at four).

### Claude's Discretion

Two areas grounded in this session's measurements rather than asked.

- **D-18:** **The SDP leg is gated on `write_execute`, and all six steps go to `locked_destructive` when
  `write_scope="none"`** — zero SDP ops in `Plan.steps`, six `(op, reason)` entries on
  `locked_destructive`, which is research R5's own prevention text. This is safe and self-consistent:
  `locked_destructive` entries **do** count toward `M` (`count_applicable`), so `N < M` and the banner
  fires, matching D-15's polarity. Note `write_scope="none"` is unreachable from `dev test` since Phase
  121's reversal (`_resolve_write_scope` returns only `"full"`/`"partial"`), so this is library/test
  surface — say so rather than implying it gates a live path.

- **D-19:** **The inhibited-write payload gets its own named generator, and a lint-style test asserts it
  is not `generate_pattern`'s output for the plan's region** (P-01 prevention 3). `B = bytes(~x & 0xFF
  for x in A)`. The committed assertions are P-01's five: equal lengths; differ at **every** byte (not
  "somewhere" — a one-page lock leak must be detectable); `B` is neither all-`0x00` nor all-`0xFF`; `A`
  likewise. A nonce or timestamp is rejected — it breaks reproducibility and the `dedup_fingerprint`
  hash. **This is the milestone's headline pitfall: `generate_pattern` is a pure function of
  `(start, length)`, so the idiomatic implementation makes A and B byte-identical and the oracle a
  tautology that looks correct in review.**

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

`ROADMAP.md` carries no `Canonical refs:` line for this phase; this list is accumulated from the ROADMAP
entry body, `REQUIREMENTS.md`, the research spine, Phase 133's outputs, and this session's live scout.

### Milestone contract (read first)
- `.planning/REQUIREMENTS.md` §"The `dev test` SDP Leg — the Oracle (LEG)" (lines 186–276) — **LEG-01,
  02, 03, 04, 05, 06, 07, 08, 12, 13, 14, 16, 17, 18 are this phase's fourteen and the only fourteen.**
  LEG-09/10/11/15 are already `[x]` (Phase 133) — do not re-tick or re-evidence them.
- `.planning/REQUIREMENTS.md` §"⚠ Evidence Ceiling" (lines 14–40) — must not be smoothed over in any
  artifact. Load-bearing here: **a locked die is unrepresentable in either repo's stubs**, so no fixture
  in this phase simulates real inhibition — fixtures pin the host's *response* to a scripted read-back.
  The causal claim *"the lock inhibited the write"* is **NOT provable this milestone**.
- `.planning/REQUIREMENTS.md` §Out-of-Scope, the `eprom_operations.py` ring-fence row — operator
  decision 2026-08-03 → `FUT-MYPY-02`. D-01 turns on it. Do not reopen.
- `.planning/ROADMAP.md` §"Phase 134: The Plan-Derived SDP Oracle in `dev test`" (lines 545–594) — the
  goal, the 5 success criteria, and the cross-cutting rule to **list this phase's own acceptance criteria
  explicitly, not incidentally**, and to **name at dispatch exactly which of the 14 requirements each
  plan may mark Complete** (executors did this prematurely 4× in Phase 116).
- `.planning/ROADMAP.md` §"Phase 137: Close" (line 678) — read for the **boundary**: CLOSE-03 owns the
  `tools/` string-literal scanner D-13 defers to, and CLOSE-06's blocking operator wording review is
  where D-16's gh#20 reply lands.

### The research spine — cite by P-number, never by phase number
- ⚠ **`.planning/research/SUMMARY.md` §"Phase 133" (line 726) IS THIS PHASE** (the oracle). Its
  §"Phase 134" is `write --sdp-relock` (Backlog 999.28) and its §"Phase 135" is channel gating. **Never
  use research's phase headings for scope.**
- `.planning/research/PITFALLS.md` §**P-01** (line 39, CRITICAL headline) — the vacuous-oracle trap.
  D-19 implements its three preventions.
- `.planning/research/PITFALLS.md` §**P-02** (line 82) — `_diff_offsets` reports zero differences for an
  empty read-back. D-04's length gate.
- `.planning/research/PITFALLS.md` §**P-03** (line 131) — three ways `_dispatch_multi_run` makes the
  write's bool the oracle. ⚠ **its prevention 4's `(False, A) ⇒ OK` is OVERTURNED by D-01/D-03.**
- `.planning/research/PITFALLS.md` §**P-04** (line 176) — the six laundering routes R1–R6 plus R7 (the
  banner). D-15 and D-17.
- `.planning/research/PITFALLS.md` §**P-05** (line 227) — the idempotent-baseline false green. D-07.
- `.planning/research/PITFALLS.md` §**P-06** (line 255) — emission claim read as state claim; prevention
  3's no-boolean rule is D-10's.
- `.planning/research/PITFALLS.md` §**P-08** (line 317) — the notice under-describes the run and its test
  checks no content. D-09.
- `.planning/research/PITFALLS.md` §**P-09** (line 344) — **the eight downgrade routes D1–D8 and the
  no-default truth table.** The single most important section for this phase.
- `.planning/research/PITFALLS.md` §**P-10** (line 389) — the capability predicate as escape hatch; a
  chip moves ALLOW→REFUSE only for a *decode* reason, never a test outcome.
- `.planning/research/PITFALLS.md` §**P-07** (line 287) — put logic in `chip_test.py` (scanned in full),
  not `cli_handlers.py` helpers (fail-open allow-list). Its `_HANDLER_FUNCTION_NAMES` derived-subset test
  landed in Phase 131 (GATE-10), so a new handler helper **is** now caught — but D-09/D-12/D-15's
  handler-side edits should still stay minimal.
- `.planning/research/FEATURES.md` §1.1–1.4 (lines 40–108) — op names, per-step report text, the
  `StepResult.op` consumer census, and **§1.4: the engine has no flags channel today**
  (`_dispatch_multi_run` passes no `operation_flags`); step 3 must import `FLAG_SKIP_SDP_UNLOCK`
  (`constants.py:136`, `0x100`) and pass it, deliberately narrowing the module's "sets no VPP, builds no
  wire dict" contract rather than silently violating it.
- `.planning/research/FEATURES.md` §2.1–2.6 (lines 112–172) — the status vocabulary (⚠ **a sixth status
  is an anti-feature**), the ten-branch outcome matrix, **§2.4's ambiguous `write_eprom` bool** (D-01's
  basis), §2.5's multi-run policy, and **§2.6: the chip-ID gate is structurally vacuous** (D-17).
- `.planning/research/FEATURES.md` §3.1–3.2 (lines 176–199) — the recovery wording, both forms, and the
  Ctrl-C caveat. D-12.
- `.planning/research/STACK.md` §"Trap 1" (line 422) — the partial-change fixture shape.

### The immediate predecessor (its outputs are this phase's inputs)
- `.planning/phases/133-sdp-leg-mechanism/133-CONTEXT.md` — D-01…D-16. Load-bearing here: **D-01** (the
  frozen `_dispatch_sdp` signature), **D-03** (SDP ops excluded from `_MULTI_RUN_OPS`), **D-06** (the
  cleanup registry), **D-11** (`_DESTRUCTIVE_OPS` asymmetry — `OP_SDP_LOCK` in, `OP_SDP_UNLOCK` out, as
  forward-protection for *this* phase), **D-12** (the parity table and its five Phase-134 exemption rows),
  **D-15** (⚠ its file-budget arithmetic is inverted — correction 4).
- `.planning/phases/133-sdp-leg-mechanism/133-RECORD.md` — the closing record. §2's D-05/D-07/D-10/D-16
  non-literal honourings, §4's ten corrections, §5's **six residuals** (two of which this phase owns:
  residual 2 = D-16's non-visible failed unlock, closed by LEG-12; residual 4 = the still-unowned
  watermark ratchet), §6's Evidence Ceiling wording to reuse verbatim.
- `.planning/phases/133-sdp-leg-mechanism/133-CI-PARITY.md` — §4's certifying **`mypy errors: 33
  (watermark: 35)`, `checked 124 source files`** and §5's file-count accounting (⚠ read alongside
  correction 4). The headroom this phase spends against is **2**.
- `.planning/phases/133-sdp-leg-mechanism/deferred-items.md` — the four pre-existing `ruff` failures in
  `tools/` (outside CI's `ruff check firestarter/ tests/` scope) and the 32→33 mypy attribution.
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-PARITY.md` and
  `firestarter_app/tools/ci_parity.sh` — the four-leg recipe. `firestarter_app/tools/ci_replica_venv.sh`
  is the **only** local path to a real mypy count (the devcontainer's own run exits 2 against numpy).

### Live code this phase edits or must not break
- `firestarter_app/firestarter/chip_test.py` — **1544 lines.** `address_fold_byte` **`:53`**;
  `generate_pattern` **`:64`**; `prepass_images` **`:75`**; `_diff_offsets` **`:98`** (P-02);
  `_FF_RATIO_THRESHOLD` **`:127`**; `classify_fingerprint` **`:143`**; op constants **`:294-300`** (seven
  shipped) and **`:309-310`** (`OP_SDP_LOCK`/`OP_SDP_UNLOCK`); `Step` **`:314`**; `Plan` **`:343`**;
  `derive_plan` **`:409-596`**; `_top_anchored_or_default` **`:599`**; `_DESTRUCTIVE_OPS` **`:663`**;
  `_MULTI_RUN_OPS` **`:690`**; `_SDP_OPS` **`:703`**; `_DESTRUCTIVE_GATE_REASON` **`:705`**;
  `StepResult` **`:711`**; `_skip_result` **`:734`**; `_resolve_or_none` **`:738`**; `run_plan`
  **`:773-972`**; `_id_step_closes_gate` **`:974`**; `_WRITE_REGION_LENGTH` **`:994`**;
  `_UV_WRITE_REGION_LENGTH` **`:1000`**; `_write_region_for` **`:1009`**; `_run_step` **`:1040`**;
  `_dispatch_step` **`:1118`**; `_dispatch_multi_run` **`:1277`** (its terminal `AssertionError`
  **`:1368`**); `_dispatch_sdp` **`:1423`**; `_RAN_VERDICTS` **`:1500`**; `count_applicable` **`:1520`**.
  **Re-measure every number at plan time** (Phase 132 D-11's discipline — 133's anchors drifted twice).
- `firestarter_app/firestarter/diagnostic_report.py` — 532 lines. `SCHEMA_VERSION` **`:55`**;
  `AutoCapture` **`:82`**; `dedup_fingerprint` **`:186`**; the disposition/ladder constants
  **`:233-249`**; `build_db_diff` **`:274`**; `DiagnosticReport` **`:318`** (its `_step_dict`, `to_dict`
  **`:444`** and `render`). D-10/D-11 edit here.
- `firestarter_app/firestarter/cli_handlers.py` — **in the mypy STRICT island.** `_VERDICT_EXIT_CODES`
  **`:1891`** and `_verdict_code` **`:1900`** (D-14); `_resolve_write_scope` **`:2019`**;
  `_ALWAYS_WRITES_NOTICE` **`:2071`** (D-09); `dev_test` **`:2085`** (its docstring's exit contract at
  `:2119-2121` is one of correction 3's two false claims); `derive_plan` call **`:2138`**;
  `read_hardware_revision_value` **`:2150`** (the first thing that energises); `run_plan` call
  **`:2164`**; `count_applicable` call **`:2166`**; the exit computation **`:2216-2219`** (D-15).
- `firestarter_app/firestarter/eprom_operations.py` — **RING-FENCED.** `EpromOperator` **`:285`**;
  `_operation_context`'s `finally` → `_disconnect_programmer` **`:405-416`** (correction 1's basis);
  `read_eprom` **`:650`**; `write_eprom` **`:1583`** (`operation_flags` param `:1588`, the `0x86` ack
  check **`:1654-1662`**); `verify_eprom` **`:1675`**; `erase_eprom` **`:1711`**; `sdp_unlock`
  **`:1736`**; `sdp_lock` **`:1784`**.
- `firestarter_app/firestarter/sdp_capability.py` — `SDP_PROTOCOL_ID = 13` **`:58`**; the reason
  constants **`:180-184`**; `sdp_capability_for_entry` **`:201`**; **`sdp_capability(chip_name, db) ->
  tuple[bool, str]` `:266`** — the derivation source for LEG-01/02.
- `firestarter_app/firestarter/sdp_honesty.py` — `unreadable_state_caveat()` **`:33`**,
  `emission_summary()` **`:45`**, `map_unknown_cmd_to_outdated()` **`:67`**. **Phase 132 D-02 built this
  as a forward contract for exactly this phase's report rows — call it, do not re-author the wording.**
  It is in the mypy strict island.
- `firestarter_app/firestarter/constants.py` — `FLAG_SKIP_SDP_UNLOCK = 0x100` **`:137`**;
  `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` **`:72-73`** and their `COMMAND_NAMES` entries **`:90-91`**.
- `firestarter_app/tests/test_op_registration_parity.py` (133-06) — **its stale-row guard fails CLOSED**,
  so its five Phase-134 exemption rows must be discharged (removed as the real registration lands) in the
  same commits, and `_DECLARED_REGISTRY_COUNT` re-asserted.
- `firestarter_app/tests/conftest.py` — `make_app_context(...) -> AppContext` **`:229-237`**,
  `app_context` fixture **`:325`**, plus `build_frame`, `_FakeSerial`, `make_comm`.
- `firestarter_app/tests/test_chip_test_sdp_leg.py` (133-01/02/03/04) — the leg's existing test module;
  extend it or add a sibling. `tests/test_chip_test.py` is 1958 lines with 10 `run_plan` call sites.
- `firestarter_app/tests/test_dev_test_cmd.py` — `test_always_writes_notice_is_the_first_line_
  unconditionally` (D-09's ordering pin) and the `write_eprom.assert_not_called()` idiom D-17 extends.
- `firestarter_app/tools/check_mypy_watermark.py` — `MIN_CHECKED_SOURCE_FILES = 120` **`:48`**
  (correction 4). `firestarter_app/pyproject.toml` — the watermark comment and the strict islands.

### Pattern precedents to copy
- `firestarter_app/tests/test_sdp_table_parity.py` — the house parity shape, incl.
  `test_altered_temp_copy_fails_parity_non_vacuous` **`:301`**.
- `firestarter_app/tests/test_skip_census.py` — `ALLOWED_SKIP_REASONS` fails **closed** on any new skip
  reason. This phase should need **none**; if a fix wants one, re-examine the fix (P-09 prevention 5).
- `firestarter_app/tests/fixtures/planted_permit_by_default.py` and `planted_widenable_allowset.py` with
  `tools/check_sdp_capability_invariants.py` — the planted-fixture idiom; **extend, never bypass**
  (P-09 D4).

### Milestone design intent (background, not a spec)
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` — ⚠ its step table was **invalidated
  by research** and its line numbers are superseded. Read for intent only.
- `.planning/notes/dev-test-design-decisions.md` — the engine's own decision record
  (`Step`/`Plan`/`run_plan`, the destructive gate, the N-of-M banner).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`classify_fingerprint` + `_diff_offsets`** (`:143`, `:98`) — the one mandated divergence primitive.
  D-04 consumes it for content-degeneracy only, **behind** a length gate; never as the equality oracle.
- **`run_plan`'s existing NA mechanism** (`Step(supported=False)` → `_skip_result(..., verdict=
  VERDICT_NA)` with no operator call) — LEG-02 needs **zero** new machinery, only `derive_plan` emitting
  the six steps with `supported=False` and `sdp_capability()`'s own reason text. The 41 refusal reasons
  are already user-facing prose.
- **`_id_step_closes_gate`** (`:974`) — D-08's structural template for the baseline gate.
- **`_dispatch_multi_run`'s guard → branch → terminal `AssertionError`** (`:1320`, `:1368`) and
  **`_dispatch_sdp`'s clone of it** (`:1423`) — every new arm inherits this shape; P-09 prevention 1's
  "no default arm, terminal raise" is already the house idiom.
- **`sdp_honesty.py`** — the emission-only caveat wording, built in Phase 132 as a forward contract for
  this phase's report rows. Do not re-author the sentences.
- **Phase 133's cleanup registry** — a successful `sdp-lock` step registers its unlock, drained in
  `run_plan`'s `finally`. This phase's step-4 unlock must not double-fire against it (133 D-11 rejected
  the both-paths shape *because* of the double-count and the endurance notice — resolve it explicitly).
- **`tests/conftest.py`'s typed `make_app_context`/`app_context`** — the new tests' fixture base.

### Established Patterns
- **Fail-closed dispatch with an explicit terminal refusal**, never a bare `else`. The pre-Phase-121
  shape routed any unmapped op to `erase_eprom()` and reported OK.
- **Module constants, never DB fields, for anything that widens a blast radius** (`_WRITE_REGION_LENGTH`
  / `_UV_WRITE_REGION_LENGTH`, SC4). The B-pattern generator and the recovery strings follow this.
- **`StepResult.op` is the axis; no new `Step`/`StepResult` field** unless a requirement forces it
  (`write-partial`'s precedent, and 133 D-05 rejected `Step.group` on exactly this ground). D-10's
  report field is a `DiagnosticReport` field, not a `StepResult` one.
- **A pre-authored gate leg proves nothing until it is seen to pass** — D-13's handoff to CLOSE-03
  follows from this, as does the rule that RED must not cross a phase boundary.
- **`reason` is invisible on the console.** `render()` shows `op`/`verdict`/`error_code`/`fingerprint`
  only; `reason` reaches the markdown table and JSON. D-07's whole basis, and it constrains every
  "put the detail in `reason`" instinct.
- **Import-time binding is pervasive** — `FW_ROOT`, `FW_REPO_PRESENT`, `_BOARD_CHOICES`,
  `channel.is_prerelease_build()` freeze at import/collection; `monkeypatch.setenv` runs after.
  Anything simulating a different environment needs a subprocess.

### Integration Points
- **`cli_handlers.py:2161-2163`** — the only production consumer of `run_plan`'s return value, and where
  133 D-07's forfeited-report residual lives. D-12's Ctrl-C caveat is the same line.
- **`cli_handlers.py:2213-2216`** — the exit computation D-14 and D-15 both change.
- **`diagnostic_report.py`'s `to_dict()`/`render()`** — LEG-12's two surfaces, and the text that reaches
  strangers on every run. No gate scans it today; CLOSE-03 will.
- **`tests/test_op_registration_parity.py`'s exemption table** — the mechanical link back to Phase 133;
  its stale-row guard turns a rename into a RED gate, by design.

### Measured live this session (re-verify at plan time; do NOT inherit)
- `firestarter_app` is on **`gsd/v1.30-sdp-surface-retirement`** @ `57e8eb5`. **The meta repo is on
  `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`** — the branch names deliberately diverge;
  check out the submodule's milestone branch before dispatching executors.
- **mypy headroom is 2**: `mypy errors: 33 (watermark: 35)`, `checked 124 source files` (floor 120).
  `chip_test.py`/`diagnostic_report.py` are in neither strict island and the global has
  `check_untyped_defs = false`; **`cli_handlers.py` IS strict** (`disallow_untyped_defs = true`), so
  every new handler-side helper needs full annotations. Measure with `tools/ci_replica_venv.sh`.
- **90 test files**, **1338 tests passing**, coverage **81.84%** against the 70% floor.
- **All 43 ALLOW chips have `chip-id == 0`** — the destructive gate is vacuous for this population
  (D-17). For a non-UV ALLOW chip `write_scope="full"` yields `write_region = (0, 256)`.
- ⚠ **`.planning/codebase/TESTING.md` is severely stale** — it asserts "the project has **no** Python
  unit tests" and references `/home/henrik/dev/...` paths. Do not use it; the `plan:pre` drift gate is
  non-blocking and will not stop a planner from believing it.

</code_context>

<specifics>
## Specific Ideas

- **This phase's durable value, stated for the record:** it is the phase that makes a `dev test` report
  from a stranger's bench *mean something* about SDP — and the phase that guarantees the same run does
  not leave their part locked. Plan it around the oracle's non-vacuity and the baseline gate, not around
  "wire up four ops and a report row".
- **The two criteria most likely to be quietly mis-satisfied are 1 and 2.** Criterion 1 because D-06
  makes its "four-step" count wrong and the temptation is to assert four and quietly ship six; criterion
  2 because its "exit code 1" is provably unreachable on a marginal-bearing run until D-14 lands, and the
  temptation is to test the exit code on a marginal-free happy path and call it discharged.
- **gh#20 is the argument, not an aside.** A real community report, host `3.0.0b14`, with `write` and
  `verify` already BAD. Without D-08's gate, running this phase's leg on that bench emits a lock at a
  part that cannot be rewritten. Every plan touching the baseline should be able to name that.
- **P-01 is the pitfall that ships silently.** `generate_pattern` is a pure function of
  `(start, length)`; the idiomatic implementation makes A and B identical and the milestone's central
  assertion a tautology that reads as correct in review. D-19's "differ at **every** byte" assertion is
  the acceptance criterion, not a nicety.
- **Discharge Phase 133's five parity exemption rows in the same commits that make them false.** The
  stale-row guard fails closed — a rename or a half-done discharge is a RED gate, which is the design.
- **Run the CI-parity recipe before and after**, and note it has **no no-board leg** — the no-board
  condition is ambient (`133-CI-PARITY.md` §1), so record the board state rather than claiming a leg.
- **At dispatch, name the allowed requirement IDs per plan.** LEG-01…08, 12, 13, 14, 16, 17, 18 — and
  explicitly **not** LEG-09/10/11/15, which are already ticked, nor any RELOCK/CHAN/CLOSE row.

</specifics>

<deferred>
## Deferred Ideas

- **The `tools/check_*.py` host-side string-literal claim scanner** over `diagnostic_report.py` —
  **Phase 137, CLOSE-03.** D-13 hands it the SDP recovery constant names so it extends rather than
  duplicates the pytest.
- **The gh#20 public reply** — **Phase 137**, behind CLOSE-06's blocking operator wording review, with
  the gh#12 reply. This phase records the finding only (D-16).
- **The underlying AT28C256 write/verify/blank-check failure** in gh#20 — a real, still-open defect that
  this phase only *triages*. **To be filed as a backlog item with a named owner** (D-16) so it does not
  become another unowned acknowledgement.
- **The `dedup_fingerprint` discontinuity's outward description** — release notes, **Phase 137**
  (CLOSE-05). Recorded as a cost here (D-11).
- **`write --sdp-relock`** — Backlog **999.28** by operator decision 2026-08-03; the pending todo
  `write-sdp-relock-deferred.md` tracks it and its stale "v1.23+" label (RELOCK-07, re-homed to Phase
  137).
- **Ratcheting the mypy watermark to the measured count** — Phase 132 D-09 recorded 32 without setting
  it, 133 measured 33, and it is **still unowned** (133-RECORD residual 4). Not this phase's to adopt
  unasked, but it is now at 2 of headroom.
- **Adding this phase's new test modules to the mypy test strict-island** — the Phase 132 D-02
  "strengthen from birth" precedent argues for it; with 2 slots of headroom, measure first and do not
  spend headroom on a strengthening this phase was not asked to perform (133-RECORD residual 5).
- **133 D-07's forfeited report on Ctrl-C** — fixing it needs `run_plan`'s signature and all twelve call
  sites. **No owner**, explicitly not adopted here; D-12 states the residual instead.
- **Refreshing `.planning/codebase/TESTING.md`** — a `/gsd-map-codebase` task. It will mislead any agent
  that reads it in the meantime.
- **The four pre-existing `ruff` failures in `tools/`** (`audit_coverage_matrix.py:37`,
  `catalog/codegen.py:36`, `catalog/codegen_vectors.py:32`/`:189`) — outside CI's
  `ruff check firestarter/ tests/` scope entirely. A lint-debt sweep, not this phase.

### Reviewed Todos (not folded)

`todo.match-phase 134` returned **15 pending, 15 matches at score 0.60; none folded.** Twelve are keyword
noise against a host-only report/oracle phase — five firmware items
(`skip-vpp-error-and-warning-checks…`, `cobs-decoder-framelevel-deadline-wr01`,
`avrdude-mcu-detection-fallback`, `remove-dead-json-init-sizeof-pointer-bug`,
`spike-databuffer-size-speed-delta`), three bench/board items (`photograph-modified-rev-0`,
`fix-jp4-labels-and-rev2-revision-block`, `write-modifications-md-rework-trace`), and four low-relevance
adjacents (`decode-infoic-flags-bits-14-15-protect-metadata` — a `build_db.py` emitter change, not a
report surface; `delete-jp5-dead-renderer`; `fold-response-code-into-log-macro`;
`prove-pio-dev-flag-fails-closed`), all matching on generic tokens like "phase", "chip", "2026", "read".

The three substantive hits are each owned elsewhere by requirement:
**`gh12-followup-after-dev-sdp-retirement`** and **`v130-close-via-pr-branch-to-beta`** are Phase 137's
close, and **`write-sdp-relock-deferred`** is Backlog 999.28 by operator decision. Note the *adjacency*
that is real but not foldable: D-16 routes this phase's gh#20 reply into the same Phase 137 operator
wording-review gate the gh#12 todo names — the coupling is recorded, the work is not moved.

</deferred>

---

*Phase: 134-The Plan-Derived SDP Oracle in `dev test`*
*Context gathered: 2026-08-04*
