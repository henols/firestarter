# Pitfalls Research

**Domain:** Host-only CLI change to a mature EPROM-programmer tool — adding a **behaviourally self-verifying SDP lifecycle** (an *inverted* assertion: a write must FAIL) to an existing community-validation command, deleting a published subcommand, and hardening two fail-open gates.
**Milestone:** v1.30 SDP Surface Retirement & Behavioral Lock Proof (phases continue at 131)
**Researched:** 2026-08-03
**Confidence:** HIGH for everything grounded in first-party source reads and locally-reproduced runs (the large majority below); MEDIUM for the two externally-sourced facts, both cross-checked against the installed library's own source.

---

## How to read this document

Every pitfall below is **specific to this milestone touching this tree**. Each carries:

- **What goes wrong** — the concrete failure, with the file/line that enables it
- **Why it happens** — usually: an existing, correct-for-its-purpose mechanism reused in a context where its polarity is wrong
- **Mechanical prevention** — a named gate, test, fixture or fail-closed construct. Not "be careful".
- **Warning signs** — what you would observe before it bites
- **Where it bit before** — the phase/milestone in this repo's own record
- **Phase to address**

Recommended phase owners use the numbering proposed in §"Pitfall-to-Phase Mapping". Phases continue at **131**.

**The two defining hazard classes are P-01…P-08 (false-green) and P-09…P-11 (inverted sensitivity).** They are treated exhaustively, ahead of everything else, because on this milestone a hollow oracle is not a quality gap — it is the milestone failing to deliver its only deliverable.

---

# PART A — The false-green magnet (exhaustive)

The leg's load-bearing assertion is that a write **does not take effect**. Every unrelated failure — transport error, brownout, absent chip, blank-check abort, closed destructive gate, capability refusal, an unmapped op — produces something the surrounding machinery already treats as "fine" or "not applicable". Below is every route in the current code by which the leg can report OK (or contribute `0` to `dev test`'s exit code) while proving nothing.

The canonical in-repo statement of this class is `tests/test_characterization.py:470-474`:

> *"cannot distinguish 'no programmer found' from 'found a real board and it refused'. Both tests patch `serial.Serial` with a MagicMock and assert it was never called, proving no port was ever opened."*

and `tests/test_dev_test_cmd.py:583`, whose SAFE-04 test names `read_hardware_revision_value.assert_not_called()` as **"the load-bearing assertion"** — the exit code was not evidence. Every prevention below is an application of that same idiom: *assert the mechanism, not the outcome.*

---

### P-01 (CRITICAL, headline): The oracle is vacuous because pattern A and pattern B are the same bytes

**What goes wrong:**
`firestarter/chip_test.py:59` —

```python
def generate_pattern(start: int, length: int) -> bytes:
    return bytes(address_fold_byte(start + i) for i in range(length))
```

`address_fold_byte` (`:48`) is `(addr ^ (addr>>8) ^ (addr>>16) ^ (addr>>24)) & 0xFF` — a **pure function of the absolute address**. `generate_pattern` is therefore a pure function of `(start, length)`. There is exactly **one** pattern per region in this engine, and `_write_region_for(step, eprom_data)` returns the region `derive_plan` already fixed once for the whole plan.

So if the implementer builds step 1 ("write pattern A") and step 3 ("write pattern B") the way every other write step in this module is built — `expected = generate_pattern(region_start, region_length)` — **A and B are byte-identical**. The oracle "read-back must still equal pattern A" then evaluates TRUE unconditionally: whether the lock inhibited the write, whether the lock did nothing, whether the write silently no-op'd, whether the chip is a brick that happens to still hold A. The single most important assertion in the milestone becomes a tautology, and it looks completely idiomatic in review because it reuses the module's blessed pattern generator.

**Why it happens:**
`generate_pattern` is the *correct* choice everywhere else in `chip_test.py` — its whole design rationale (`:51-54`) is address-fault sensitivity, which requires determinism. Reusing it is the path of least resistance and the reviewer's expectation. Nothing in the module signals that a *second, distinguishable* payload is ever needed, because until now no step needed one.

**Mechanical prevention:**
1. **A committed test that asserts the two payloads differ at every byte**, keyed off the same functions production uses — not off literals:
   ```
   a, b = _sdp_pattern_a(region), _sdp_pattern_b(region)
   assert len(a) == len(b) == region_length
   assert all(x != y for x, y in zip(a, b))        # differ EVERYWHERE, not just somewhere
   assert b != bytes(region_length)                # not all-0x00
   assert b != b"\xff" * region_length             # not blank
   assert a != bytes(region_length) and a != b"\xff" * region_length
   ```
   "Differ at every byte" (not "differ somewhere") is load-bearing: a partial lock leak that changes *one page* must be detectable, which requires the two payloads to disagree everywhere the write could have landed.
2. **Derive B by a construction that cannot collapse to A** — bitwise complement of A is the cheapest (`bytes(~x & 0xFF for x in a)`), and on a 0x0D EEPROM both bit directions are writable, so B is genuinely programmable over A. A *nonce* or timestamp is worse: it makes the report non-reproducible and breaks the `dedup_fingerprint` hash. Complement is deterministic *and* maximally distinguishable.
3. **Refuse to accept `generate_pattern` as the B source at all** — give B its own named function and add a lint-style test asserting the inhibited-write step's payload is not `generate_pattern(...)`'s output for the plan's region.

**Warning signs:**
- The inhibited-write step's plan/summary says "write pattern B" but the code calls `generate_pattern` with the same `step.write_region` as step 1.
- A native test of the leg passes on the very first attempt with no fixture that models a *leaky* lock.
- No test in the phase distinguishes "lock worked" from "lock did nothing" — because with A == B, no test *can*.

**Where it bit before:**
This is the v1.22 C-5 shape one layer down. v1.22's whole opening finding was that a check which looked like verification — the `(0x5555, 0x20)` success check — was **inverted**, not merely weak, and had shipped since v1.0. And v1.12's GATE-03 was an "asserted-empty-but-never-populated" detector; `RETROSPECTIVE.md:404` states the rule: *"A safety gate must actually be able to fail. A detector that's asserted-empty-but-never-populated is worse than no gate (false assurance)."*

**Phase to address:** the SDP-leg phase (proposed **133**), as its first plan, before any step is wired.

---

### P-02 (CRITICAL): `_diff_offsets` reports **zero differences** for an empty read-back

**What goes wrong:**
`firestarter/chip_test.py:93-104` —

```python
cmp_len = min(len(expected), len(actual))
diff_offsets = [o for o in range(cmp_len) if expected[o] != actual[o]]
pct = 100.0 * len(diff_offsets) / cmp_len if cmp_len else 0.0
```

Its docstring says explicitly: *"unequal-length inputs are compared only over their common prefix and never raise."* With `actual = b""` (a failed read-back), `cmp_len == 0`, `diff_offsets == []`, `pct == 0.0`. **A total read failure is indistinguishable from a byte-perfect match.**

This is the *one* divergence primitive the module mandates (`:86-88`: *"do NOT add a second parallel divergence implementation elsewhere in this codebase (D-04 mandate)"*), so the implementer is instructed by the code to use it. Written the obvious way —

```python
if not _diff_offsets(pattern_a, readback)[1]:
    verdict = VERDICT_OK   # "chip unchanged — lock held"
```

— a read-back that returned nothing at all reports **the lock held**. Same for a *short* read-back: 256 bytes expected, 4 bytes returned that happen to match → `[]` → OK.

**Why it happens:**
`_diff_offsets`'s never-raise, common-prefix semantics are correct for its original job (comparing two reads of unknown length for a *divergence metric*, where 0 is a safe default). Used as an *equality oracle* the same defaults invert into a false green. The polarity of "no differences found" flips depending on whether you're measuring divergence or proving equality.

**Mechanical prevention:**
1. **A length gate before any comparison**, in the leg's own code:
   ```python
   if len(readback) != len(pattern_a):
       return StepResult(op=OP_SDP_INHIBITED_WRITE, verdict=VERDICT_BAD,
                         reason=f"read-back length {len(readback)} != expected "
                                f"{len(pattern_a)} — oracle inconclusive, not a pass")
   ```
   `VERDICT_BAD`, never `SKIPPED` (see P-09 for why).
2. **A non-blank / non-empty guard**: an all-0xFF read-back is a blank/contact condition, not evidence — `prepass_images` (`:70`) exists precisely to name that condition and `classify_fingerprint` already treats all-0xFF as a blank/contact signal. Route the SDP read-back through `classify_fingerprint` too so a contact fault reads as a contact fault, not as "unchanged".
3. **A planted-fixture test per degenerate input**, each asserting BAD: `b""`, a short prefix of A, all-0xFF, all-0x00. Four cases, four asserts. Without these the oracle is untested against exactly the inputs a real bench failure produces.

**Warning signs:**
- The leg's comparison calls `_diff_offsets` (or `==` on `bytes`) without a preceding length assertion.
- A test named something like `test_lock_holds` whose fixture read-back is built from `generate_pattern` — i.e. the happy path only.
- gh#20 (AT28C256 `dev test` FAIL, open since 2026-07-30) is exactly the situation that produces degenerate read-backs on this family in the field.

**Where it bit before:**
`chip_test.py:1140-1160`'s own comment records the same swallow being *deliberately* accepted for the fingerprint: *"a readback failure … must NOT convert an otherwise successful write/verify outcome into BAD (Pitfall 1 extends to this internal readback call too) — it only means no Fingerprint could be attached."* That choice is right for a diagnostic fingerprint and **catastrophically wrong for an oracle**. Reusing that code path is P-03.

**Phase to address:** 133.

---

### P-03 (CRITICAL): Reusing `_dispatch_multi_run` makes the write's boolean the oracle — three separate ways

**What goes wrong:**
`_dispatch_multi_run` (`chip_test.py:1039-1195`) is the only place write-shaped ops execute. Routing the inhibited write through it inherits three defects at once:

**(a) The verdict is the write's return value.** `:1170-1173`:
```python
verdict = VERDICT_OK if outcomes and outcomes[0] else VERDICT_BAD
```
`outcomes` is `[operator.write_eprom(...) for _ in range(runs)]`. So the step's verdict is *"did the write report success"* — precisely the "exit-code-only" oracle the design note forbids. If the firmware's inhibited write returns `True` (it wrote nothing but reported OK, or the lock never reached silicon), the step is **OK**. If the write returns `False` for a transport reason, the step is **BAD** — right answer, wrong reason, and a maintainer reading the report cannot tell which.

**(b) `runs` defaults to 2, so the inhibited write executes TWICE.** `run_plan(..., runs: int = 2)`, and `runs < 2` is *rejected* (`:768-780`). Two attempted writes of B against a locked part means: if the lock leaks partially, run 1 changes some bytes and run 2 changes more, so the read-back state depends on how many passes ran. Worse, `marginal` fires on disagreement (`:1169-1171`) — and `marginal` maps to exit code **2**, a *third* outcome for what should be a binary claim. Worst: if both runs return the same boolean, `marginal` does *not* fire and the disagreement signal is lost.

**(c) The read-back is best-effort and swallowed.** `:1147-1160`:
```python
except EpromOperationError:
    actual = b""
...
if actual:
    fingerprint = classify_fingerprint(...)
```
A read-back failure yields no fingerprint and **leaves the write-boolean verdict standing**. Combined with (a): the write says OK, the read-back that was supposed to falsify it silently didn't happen, and the step reports OK with no fingerprint. Nothing in the report says the oracle didn't run.

**Why it happens:**
`_MULTI_RUN_OPS` is documented as the mandatory registration point: *"any future op added to the vocabulary MUST be added to both frozensets in this block or it fails closed by construction"* (`:672-676`). An implementer reading that correctly concludes "register my new ops in both frozensets" — and registering the inhibited write in `_MULTI_RUN_OPS` routes it straight into the boolean-verdict path. **The fail-closed instruction leads directly into the false-green path.** That is the trap.

**Mechanical prevention:**
1. **The inhibited-write step gets its own dispatch arm in `_dispatch_step`, above the `_MULTI_RUN_OPS` branch** — a dedicated function whose verdict is computed *only* from the read-back comparison. The write's boolean becomes a recorded *reason* field, never the verdict.
2. **`runs == 1` for the inhibited write, enforced structurally**: the new arm takes no `runs`. Assert `run_count == 1` in a committed test. A second attempted write against a possibly-leaky lock destroys the evidence the first attempt produced.
3. **Register the lock/unlock/inhibited ops in `_DESTRUCTIVE_OPS` (all three mutate or attempt to mutate) but keep the inhibited write OUT of `_MULTI_RUN_OPS`** — and add a test asserting that op is *not* in `_MULTI_RUN_OPS`, with a comment pointing at this pitfall. Otherwise a future tidy-up "completes" the registration and silently restores the boolean oracle.
4. **A deliberate-break test**: mock `write_eprom` to return `True` *and* a read-back equal to pattern **B** (i.e. the write took effect). Assert the step is `BAD`. Then mock `write_eprom` to return `False` with a read-back equal to **A**. Assert the step is `OK`. These two cases together prove the verdict is driven by the read-back and *not* by the boolean. Without both directions, the test passes on a boolean-driven implementation.

**Warning signs:**
- The new op strings appear in `_MULTI_RUN_OPS`.
- `StepResult.run_count == 2` for the inhibited write.
- The step's `reason` is empty on a pass (the boolean path sets `reason = ""`).
- A grep for the new op name finds no new `if step.op ==` arm in `_dispatch_step`.

**Where it bit before:**
Phase 121 Plan 02, RESEARCH C-5 / "Pitfall 1a": `_MULTI_RUN_OPS` had **zero references anywhere in the tree**; `_dispatch_step`'s trailing `return _dispatch_multi_run(...)` was unconditional and `_dispatch_multi_run` ended in `else: # OP_ERASE`, so **any** op string reached `operator.erase_eprom()` and reported `VERDICT_OK` — *"proven empirically: an unmapped op called erase_eprom() twice and returned OK"* (`chip_test.py:644-650`). The guard that fixed it is the same guard that now funnels new ops into the boolean-verdict path.

**Phase to address:** 133.

---

### P-04 (CRITICAL): `SKIPPED` and `NA` both map to exit code **0** — six routes to a green run with no oracle

**What goes wrong:**
`cli_handlers.py:1862-1868`:
```python
_VERDICT_EXIT_CODES = {VERDICT_OK: 0, VERDICT_NA: 0, VERDICT_SKIPPED: 0,
                       VERDICT_MARGINAL: 2, VERDICT_BAD: 1}
```
and `dev_test`'s contract (`cli_handlers.py:2091`): *"0 if every step is OK/NA/SKIPPED, 2 if any step is marginal (and none BAD), 1 if any step is BAD"*, computed as `max(...)`. **Any path that turns the oracle step into SKIPPED or NA yields `firestarter dev test <chip>` → exit 0**, and a community member reports "PASS".

Every route in the current code:

| # | Route | Mechanism | Result today |
|---|-------|-----------|--------------|
| R1 | **Chip-ID mismatch closes the destructive gate** | `run_plan:784` — `if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed: results.append(_skip_result(step.op, _DESTRUCTIVE_GATE_REASON))` | oracle step `SKIPPED` → 0 |
| R2 | **`_id_step_closes_gate` fires on ANY id uncertainty** — `result.verdict in (BAD, SKIPPED)` (`:808`) | a flaky id read, an absent chip in DB case B, a transport hiccup | oracle `SKIPPED` → 0 |
| R3 | **`resolve_chip` refusal** — `_resolve_or_none` maps `ChipNotImplementedError`/`ChipNotFoundError` → `SKIPPED` (`:696-706`) | support-status refusal on the chip | oracle `SKIPPED` → 0 |
| R4 | **`step.supported is False`** → `_skip_result(..., verdict=VERDICT_NA)` (`:781`) | a `sdp_capability()` REFUSE, or a mis-keyed applicability predicate | oracle `NA` → 0 |
| R5 | **`write_scope="none"`** — `derive_plan` structurally OMITS write/verify/erase from `Plan.steps` and puts them on `locked_destructive`; *"run_plan has no code path to iterate them"* (`:405-409`) | if the SDP steps are added outside the `write_execute` branch, you get lock-with-no-baseline-and-no-unlock; if inside, they vanish silently | either a hazard (P-13) or an invisible omission |
| R6 | **Empty `results`** — `if not results: sys.exit(0)` (`cli_handlers.py:2187`) | a `derive_plan` failure returning an empty plan | exit 0 with nothing run |

And a seventh, subtler one:

| R7 | **The N-of-M banner does not notice.** `_RAN_VERDICTS = {OK, BAD, marginal}` (`chip_test.py:1209`); `count_applicable` computes `M = sum(1 for s in plan.steps if s.supported) + len(plan.locked_destructive)` and `N = count of results whose verdict is in _RAN_VERDICTS`. An `NA` SDP step is **excluded from M as well as N**, so the headline coverage ratio stays at `N == M` while the oracle never ran. |

**Why it happens:**
`SKIPPED`/`NA` → 0 is *correct* for every pre-existing step: an inapplicable erase on a UV part is genuinely not a failure. The SDP oracle is the first step in this command whose *absence* is itself a finding — and the exit-code table has no vocabulary for that.

**Mechanical prevention:**
1. **A distinct verdict or a distinct reporting slot for "the oracle did not run on a chip where it applies".** Concretely: when `sdp_capability()` returns ALLOW, a `SKIPPED` oracle step must be surfaced, not absorbed. Options, in order of preference:
   - Add the SDP oracle result to `DiagnosticReport` as a **named, always-present field** (not just another row in `results`), rendered on every ALLOW-chip run as one of `HELD / NOT-HELD / NOT-RUN(reason)`. `NOT-RUN` is then visible in the JSON artifact and in the filed issue even at exit 0.
   - And/or: map an `ALLOW`-chip oracle `SKIPPED` to exit **2** (`marginal`) rather than 0 — "we tried and could not tell" is genuinely marginal.
2. **A test per route R1–R6**, each asserting the *observable* outcome, in the SAFE-04 idiom:
   - R1/R2: mock a chip-ID mismatch. Assert `operator.sdp_lock.assert_not_called()` **and** that the report's SDP field reads `NOT-RUN` with the gate reason. `test_dev_test_cmd.py:667-679` already does exactly this shape for `write_eprom` (`operator.write_eprom.assert_not_called()`) — extend it.
   - R4: mock a REFUSE chip. Assert `sdp_lock.assert_not_called()` and that the `reason` string carried into the `NA` step is `sdp_capability()`'s own reason text, not a generic one (the design note requires REFUSED chips get *"an `NA`/`SKIPPED` step carrying `reason`, never a silent omission"*).
   - R5: assert `derive_plan(name, db, write_scope="none")` yields **zero** SDP ops in `Plan.steps` and lists them in `locked_destructive` with a reason.
   - R6: assert an empty plan for an ALLOW chip is impossible, or that it exits non-zero.
3. **Extend `count_applicable`'s M to include the SDP oracle for ALLOW chips regardless of outcome**, so an `NA`/`SKIPPED` oracle *drops the N/M ratio* and fires the banner. Pin with a test.

**Warning signs:**
- The phase's tests assert `result.exit_code == 0` on a happy path and nothing else.
- No test mocks a chip-ID mismatch alongside the SDP leg.
- The report's Markdown table (`cli_handlers.py:2166-2172`) is the only place the SDP steps appear.

**Where it bit before:**
Phase 114.1 exists *solely* because absent-chip handling was wrong, and its fix's real assertion was `read_hardware_revision_value.assert_not_called()`, not the exit code (`tests/test_dev_test_cmd.py:576-598`). Recorded in memory as *"dev test absent-chip false-green trap — exit-code-only tests lie"*.

**Phase to address:** 133, with the report field owned jointly with `diagnostic_report.py`.

---

### P-05 (HIGH): The baseline step is non-discriminating because the pattern is idempotent

**What goes wrong:**
Step 1 is "write pattern A + verify" and exists so *"a locked-from-the-factory part cannot read as 'lock works'"*. But because `generate_pattern` is deterministic (P-01), **the second `dev test` run on the same chip finds pattern A already on the die.** A verify that passes because the bytes were already there is not evidence that the write path works — and the write path working is the entire premise of step 3's inference.

Concretely: a chip whose write path is dead but which carries A from a previous run passes step 1 (verify OK), passes step 3 (read-back == A, because nothing can ever be written), and passes step 4 (verify OK again). **A completely dead write path produces a perfect SDP leg result.** This is the single most convincing false green available, and it requires no bug — just running `dev test` twice.

**Why it happens:**
Nothing in the existing engine ever needed to prove a *transition*; it only ever needed to prove a *final state*. `verify_eprom` compares against expected bytes; it has no notion of "and these bytes changed".

**Mechanical prevention:**
1. **Prove a transition, not a state.** Before writing A, read the region and assert it is **not already** A; if it is, write the complement first, then A. Both reads/writes are already available. Record the pre-state hash in the report.
   Simpler and cheaper: **write B first, verify B, then write A, verify A.** Two transitions in opposite directions, both proven, before any lock is applied. This costs one extra write on a 256-byte or full-device region and buys the only evidence that the write path is live.
2. **A committed test with a fixture whose "chip" starts holding pattern A and whose write is a no-op.** Assert the baseline step reports BAD. Without this fixture the defect is unobservable in a test suite whose mocks always start blank.
3. **Record the pre-write read hash in the JSON artifact** so a community report contains the evidence even when the leg passes.

**Warning signs:**
- The baseline step is a plain reuse of the existing `OP_WRITE` + `OP_VERIFY` pair.
- No test starts the mock chip in a state that already matches the pattern.
- `dev test` run twice back-to-back on the same part gives identical output including timings.

**Where it bit before:**
Adjacent, and instructive: `write -b` "SKIPS ERASE, not just blank-check — silently corrupts non-blank chips, still reports 'successful'" (recorded in memory). Same shape: an operation whose success report is decoupled from whether it changed anything. Also v1.14/v1.15's insistence on *non-vacuous negative controls* (`RETROSPECTIVE.md:431`, `:467`).

**Phase to address:** 133.

---

### P-06 (HIGH): The lock step's own "success" is an emission claim and will be read as a state claim

**What goes wrong:**
`eprom_operations.py:1736 sdp_unlock` / `:1784 sdp_lock` return `bool`, and their docstrings are explicit: *"A `True` return means only that the command sequence was **emitted** over the wire — it is never a claim that silicon actually left the protected state."* Wrapped as a `StepResult`, that boolean becomes `verdict=OK` in a table headed **Verdict**, next to steps whose OK *is* a state claim. A reader of the filed issue sees `sdp_lock | OK` and concludes the chip is locked.

Then step 3's read-back-equals-A is read as *confirming* it. The two together look like a proof. They are not: on the causal claim, step 2 contributes nothing at all.

**Why it happens:**
`StepResult` has one `verdict` axis and it is overloaded. There is no "emitted / not-observable" verdict in the vocabulary.

**Mechanical prevention:**
1. **The lock and unlock steps must carry a non-empty `reason` on SUCCESS** stating emission-only and unreadability, and the report renderer must print it. A test in the `test_dev_sdp_cmd.py` mould:
   ```
   assert "cannot be read back" in <the sdp_lock row's rendered text>
   assert "not a claim about the chip's actual state" in <same>
   ```
   These are the *exact* assertions `tests/test_dev_sdp_cmd.py:395-478` already makes — see P-16 for why they must be **moved, not deleted**.
2. **Positive-framing assertion, not a forbidden-word list** — `test_no_fabricated_lock_state_boolean_in_the_report` (`:453`) records the reasoning: *"a positive framing assertion, not a brittle forbidden-substring word-list, so this leg does not rot as wording evolves."* Reuse that discipline.
3. **No boolean named `locked` anywhere in `DiagnosticReport` or its `to_dict()`.** A JSON consumer (`parse_devtest_issue.py`, the dedup fingerprint, anyone reading the artifact) will treat a JSON `true` as ground truth. Assert its absence.

**Warning signs:**
- `report.to_dict()` gains a key like `sdp_locked` or `protection_enabled`.
- The lock step's `reason` is `""` on success.
- The Markdown table's `Reason` column reads `-` for the lock row.

**Where it bit before:**
v1.22 Phase 120 HOST-05 built exactly these three assertions, and v1.22's C-5 correction was an overclaim of precisely this shape reaching *a locked project decision*. Also Phase 117 D-05 / Phase 118 D-02 / Phase 119 D-12 — three separate phases establishing that protection state is not readable on this family.

**Phase to address:** 133 (report rows) and the close phase (136) for the outward-facing prose.

---

### P-07 (MEDIUM-HIGH): `check_devtest_orchestrator.py` silently does not scan the leg's new helper

**What goes wrong:**
`tools/check_devtest_orchestrator.py:138-150` hardcodes:
```python
_HANDLER_FUNCTION_NAMES = frozenset({"dev_test", "_verdict_code", "_sanitize_chip_token",
    "_is_uv_eprom", "_resolve_write_scope", "_default_uv_write_confirm",
    "_chip_id_fields", "_is_interactive", "_make_sampler"})
```
`_scan_target_functions` (`:281-315`) fails closed **only when NONE of the names match**. A *partial* match — `dev_test` present, a new `_sdp_leg_*` helper absent from the list — scans successfully and **silently omits the new function**. So a new helper in `cli_handlers.py` that sets VPP, hand-assembles a wire dict, or passes `force=True` is invisible to the orchestrator-only gate. The gate prints `PASS:` and means nothing about the new code.

**Why it happens:**
The allow-list was scoped narrowly for a good reason (`cli_handlers.py` has 10 pre-existing legitimate `--force` flags on unrelated commands, so a whole-file scan would be permanently red). But an **allow-list of function names is fail-open against ADDITIONS** — and the docstring's fail-closed guarantee is written only about *renames and removals*, not additions.

**Mechanical prevention:**
1. **Add every new SDP-leg helper name to `_HANDLER_FUNCTION_NAMES` in the same commit that creates it** — and make that mechanical rather than remembered: add a test that derives the required set from the AST (every module-level function whose name starts with `_` and is *referenced from `dev_test`'s body*) and asserts it is a subset of `_HANDLER_FUNCTION_NAMES`, naming any omission. This converts an additive fail-open into an additive fail-closed.
2. **Prefer putting new logic in `chip_test.py`, which is scanned in FULL** (`_scan_file`, `:58`: *"`chip_test.py` is unaffected and still scans the ENTIRE file"*). Keeping the leg's logic in the engine and the handler thin sidesteps the allow-list entirely. This is also the right architectural placement.
3. **Re-run the checker with a planted violation inside a NEW helper name** as part of the phase's acceptance — proving the gate can see the new code, not just the old code. `tests/test_check_devtest_orchestrator.py` already has the `FIRESTARTER_DEVTEST_SRC`/`FIRESTARTER_DEVTEST_HANDLER` seams for this.

**Warning signs:**
- New `_`-prefixed functions in `cli_handlers.py` and no diff to `tools/check_devtest_orchestrator.py`.
- `python3 tools/check_devtest_orchestrator.py` still prints `PASS:` after the leg lands, with no new function names in its output.

**Where it bit before:**
The general class is documented in this repo as *"App gates scan FIRMWARE source — renames break them ... they fail OPEN"* (4× in Phase 117), and Phase 123 BASE-02/D-09 removed the same fail-open shape from **seven** host test modules. `.planning/STATE.md:701-703` warns the `_FW_ABSENT` idiom was fixed for the host suite in Phase 123 but *"six modules shared it — worth confirming none survive."*

**Phase to address:** the gate-hardening phase (proposed **131**) for the derived-subset test; 133 for the additions themselves.

---

### P-08 (MEDIUM): The always-writes notice under-describes the run, and its test does not check content

**What goes wrong:**
`_ALWAYS_WRITES_NOTICE` (`cli_handlers.py:2042-2049`) currently promises:

> *"Every write/verify/erase step runs TWICE per invocation, so most chips receive the full device written twice"*

After the leg, an ALLOW-listed AT28C receives **three or four** additional write passes plus a lock, and the part may be **left locked on abort**. The committed test `test_always_writes_notice_is_the_first_line_unconditionally` (`test_dev_test_cmd.py:244`) asserts only that the notice is *first* and *unconditional* — **not what it says**. So the notice can silently become false while its test stays green, and the false notice is the first thing a community member reads before consenting to sacrifice a chip.

**Mechanical prevention:**
1. Update the notice, and add a content assertion: it must name the SDP lock, must state the part is left unlocked on a *completed* run, and must state the recovery for an *aborted* run in the words "rewrite" (see P-14).
2. A test asserting the notice's write-pass count matches the plan the engine actually derives for a representative ALLOW chip — i.e. derive it, don't hardcode the sentence twice.

**Where it bit before:** Phase 121 D-04 introduced the notice precisely because the destructiveness had changed and the old wording was stale.

**Phase to address:** 133.

---

# PART B — Inverted sensitivity (exhaustive)

> *"If the lock never reaches silicon (the v1.22 defect class), the inhibited write **succeeds** — and the leg must then report BAD. An unexpected success is the failure signal, never an inapplicable step; it must never be allowed to downgrade to `SKIPPED`/`NA`."* — PROJECT.md, trap 2

This is not a hypothetical defect class. v1.22 established that the SDP-**disable** sequence *"has shipped since v1.0-era Phase 06-01 … and almost certainly never reached silicon"* because `/WE` was emitted HIGH — a documented Write Inhibit — on all four `0x0D` pinouts, across all 84 `0x0D` chips. The lock half (Phase 119) has never been exercised on silicon at all. **The most likely real-world outcome of step 3 is that the write succeeds.** The leg exists to say so.

---

### P-09 (CRITICAL): Every route by which an unexpected SUCCESS gets downgraded

Enumerated, because each is a plausible implementer choice that individually looks defensible:

| # | The downgrade | Why an implementer would do it | Why it inverts the leg |
|---|---|---|---|
| D1 | **"The write succeeded, so the lock must not be supported on this part — mark `NA`."** | Mirrors `derive_plan`'s existing NA-on-inapplicable convention, and feels charitable. | This is the *finding*. Turning the finding into "inapplicable" deletes it. `NA` → exit 0. |
| D2 | **"The write succeeded, so we can't test the lock — mark `SKIPPED`."** | Mirrors `_resolve_or_none`'s refusal→SKIPPED mapping. | Same: `SKIPPED` → exit 0. |
| D3 | **"The lock emission returned False, so skip the oracle."** | Defensive: don't test what didn't set up. | A failed lock *emission* is itself a BAD finding, and skipping the oracle hides whether the write then succeeded. Report BOTH: lock emission BAD **and** oracle run anyway (a write attempt on an unlocked part is exactly what `dev test` already does, so it adds no risk). |
| D4 | **Auto-widening the capability predicate on error.** `sdp_capability()` returning ALLOW-by-default on an exception or a missing DB field. | An unexpected exception "shouldn't fail the run". | Permit-by-default on the applicability predicate. There is already a planted fixture for this class: `tests/fixtures/planted_permit_by_default.py` and `planted_widenable_allowset.py`, enforced by `tools/check_sdp_capability_invariants.py`. Extend those, don't bypass them. |
| D5 | **Treating `marginal` as the landing zone.** Two runs disagree → `marginal` → exit 2, which "isn't a failure". | `_dispatch_multi_run`'s existing D-06 policy. | For a *binary* causal claim, `marginal` is a laundering channel. Solved by P-03's `runs == 1`. |
| D6 | **A `try/except Exception: pass` around the oracle** so the leg "never breaks the run". | `run_plan`'s Pitfall-1 contract genuinely is *"one step's BAD verdict or exception NEVER aborts the remaining steps"* (`:734-737`), and `_sample`'s `except Exception: pass` (`:1036-1040`) is a committed precedent. | Non-fatal ≠ silent. Non-fatal means *record BAD and continue*. `_sample`'s swallow is correct because a sampler is a diagnostic; the oracle is not a diagnostic. |
| D7 | **Reporting the oracle as a `divergence` metric instead of a verdict.** `_dispatch_read`'s D-06 policy: *"read-step disagreement across runs is a byte-level divergence metric … NEVER a verdict flip and NEVER `marginal`"* (`:983-990`). | It's the module's stated policy for read disagreements, and the oracle *is* a read comparison. | That policy is about *repeat-read flakiness*, not about a *deliberate* expected-vs-actual comparison. Applying it makes the oracle produce a number nobody gates on. |
| D8 | **Suppressing the finding because `0x0D` is `UNVERIFIED` anyway.** | "We already know it's unverified, so a BAD here is expected noise." | Then the leg has no purpose. A BAD here is the first actionable evidence the feature has ever produced. |

**Mechanical prevention (one construct, several assertions):**

1. **A single explicit truth table in the leg's code, with no default arm**, e.g.:

   | read-back == A | read-back == B | read-back == something else | length/blank bad |
   |---|---|---|---|
   | `OK` — lock held (emission-only caveat still applies) | `BAD` — **lock did not inhibit the write** (the v1.22 defect class) | `BAD` — **partial change**, gh#11's exact symptom | `BAD` — oracle inconclusive |

   Four arms, all four reachable, **none of them `NA`/`SKIPPED`/`marginal`**, and a final `raise AssertionError` for anything unclassified (the shape `_dispatch_multi_run:1130` already uses for its unreachable arm).

2. **A committed test per arm, with the "write succeeded" arm asserting `verdict == VERDICT_BAD` and `exit_code == 1`.** This is the single most important test in the milestone. It must exist as a *named, listed acceptance criterion*, not an incidental case.

3. **A "polarity pin" test that would fail if the arms were swapped** — assert the BAD arm's `reason` text contains the causal statement ("the write was not inhibited") and the OK arm's does not. A reviewer reading a diff that inverts the comparison must see two tests go red, not one.

4. **A grep-style gate over the leg's source forbidding `VERDICT_NA`, `VERDICT_SKIPPED` and `VERDICT_MARGINAL` inside the oracle function** — mechanical, three lines, and paired with a planted-violation fixture in the house style (`tests/fixtures/planted_*.py`).

5. **`tests/test_skip_census.py` is a free ally here.** Its `ALLOWED_SKIP_REASONS` frozenset means any *new* pytest skip reason introduced by this milestone **fails the census** unless deliberately added with a comment (`test_every_skip_reason_is_allow_listed`). Do not add an entry for anything SDP-related without an explicit, reviewed justification — and note the census asserts a *non-zero collected count* (`test_census_child_run_is_live`) precisely so a collection regression cannot silence it. Use it; don't work around it.

**Warning signs:**
- The oracle function contains the token `NA`, `SKIPPED`, `marginal`, or a bare `except`.
- The phase's test list has one "lock holds" test and no "lock does not hold" test.
- The word "expected" appears in a comment near the write-succeeded branch.

**Where it bit before:**
The v1.22 opening finding: the `(0x5555, 0x20)` success check was **inverted**, not merely weak — an oracle that reported success on the failure condition, shipped for two years. And `RETROSPECTIVE.md:404`: *"A safety gate must actually be able to fail."*

**Phase to address:** 133, as a named acceptance criterion.

---

### P-10 (HIGH): The applicability predicate becomes the escape hatch

**What goes wrong:**
`sdp_capability(chip_name, db)` (`firestarter/sdp_capability.py:266`) is the fail-closed allow-set: **43 ALLOW / 41 REFUSE of 84** `0x0D` chips. When the leg reports BAD in the field on, say, an AT28C256, the cheapest way to make the report green is to move that chip to REFUSE. That converts a real finding into an `NA` step at exit 0 and quietly retires the only evidence path the feature has.

**Mechanical prevention:**
1. `tools/check_sdp_capability_invariants.py` + `tests/fixtures/planted_widenable_allowset.py` already gate *widening*. **The missing gate is against NARROWING for convenience.** Add a committed count assertion — `43 ALLOW / 41 REFUSE / 84 total`, derived not literal — so any partition change is a visible, justified diff, and pin the derivation source (`infoic.xml` `flags` bit 15) rather than a hand list.
2. `tests/test_sdp_db_invariant.py` and `test_sdp_table_parity.py` exist; extend the parity assertion to the counts.
3. **A note in the ledger:** a chip may only move ALLOW→REFUSE with a *decode* reason (its `flags` bit changed / the decode was wrong), never with a *test-outcome* reason.

**Where it bit before:**
The 43/41 partition was taken **at operator directive** in v1.22 Phase 120 as a *derived* set, precisely to prevent hand-curation. `.planning/STATE.md:920` records the SEVENTH PROJECT.md correction documenting the derived provenance.

**Phase to address:** 131 (the count gate) and 133 (the leg's use of it).

---

# PART C — Overclaiming at close, and the claim-gate reuse question

### P-11 (CRITICAL): Naively copying `check_permitted_claims.py` produces a gate that **PASSES while scanning v1.23's artifacts**

This is the direct answer to the milestone's claim-gate question, and the answer is: **neither existing copy is safe to copy verbatim, and the v1.23 copy is the more dangerous of the two.**

**The two copies on disk** (both committed to the meta repo, both with paired tests and planted fixtures):

| | `.planning/phases/122-close-…/check_permitted_claims.py` (9.4 KB) | `.planning/phases/123-non-regression-…/check_permitted_claims.py` (~14 KB) |
|---|---|---|
| Domain of `FORBIDDEN_PATTERNS` | **AT28C / SDP / silicon** — `verified-fixed`, `confirmed-working`, `silicon-verified`, `verified-on-silicon`, `works-on-silicon`, `now-works`, `should-now-work`, `proven-on-silicon` | **PY32F071** — `runs-on-py32`, `works-end-to-end`, `flashed-a-py32`, `closed-loop-vpp`, `pin-map-correct`, … |
| `REQUIRED_CAVEAT_PROSE` | `"no AT28C silicon was tested"` | `"no PY32F071 hardware exists"` |
| Target resolution | `_HERE`-relative, 5 artifacts in its **own** phase dir | `_HERE/../130-close-honesty-ledger-claim-gate-release-decision/`, 4 artifacts in a **sibling** dir named by a string constant |
| Proximity scoping | **none** — whole-text scan | D-16 line-scoped ±1 line around a `py32` token |
| Arming | none — a missing target is always a hard failure | D-15 all-or-nothing: **zero** of 4 exist → `UNARMED:` + **exit 0**; 1–3 exist → hard failure |
| Vacuity guard ordering | missing-target check first, empty-list check after | empty-list check hoisted first (deliberate hardening over v1.22) |
| Env seam | `FIRESTARTER_CLAIMSCAN_TARGETS` | **the same name, reused verbatim** (documented as assumption A3) |

**What breaks if the v1.23 copy is copied into a v1.30 phase directory:**

`_PHASE_130_DIR = os.path.normpath(os.path.join(_HERE, os.pardir, "130-close-honesty-ledger-claim-gate-release-decision"))`. `_HERE` becomes the *new* phase's directory; `os.pardir` is still `.planning/phases/`; and **`.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/` still exists on disk with all four artifacts present.** So the copied checker:

1. resolves four **real, existing** files,
2. finds all four carry `"no PY32F071 hardware exists"` (they do — that was v1.23's requirement),
3. finds zero py32-proximate forbidden phrases (v1.23's Phase 130 made that true),
4. prints **`PASS: scanned ../130-…/130-LEDGER.md, …`** and exits **0**.

**This is strictly worse than the C-2 defect it was built to fix.** C-2 produced `UNARMED:` + exit 0 — a message that at least says nothing was scanned. A copied v1.23 checker produces a confident `PASS:` naming four real files, on a milestone whose artifacts it has never opened, using a forbidden-phrase vocabulary about a microcontroller this milestone does not touch, and requiring a PY32F071 caveat that v1.30's honest prose has no reason to contain. Every diagnostic signal points the wrong way.

Secondary breakages of a naive copy (either version):

- **Wrong vocabulary.** v1.23's eight patterns cannot detect a single SDP overclaim. v1.22's eight *can* — that copy is the right **starting vocabulary**.
- **Missing proximity scoping in the v1.22 copy.** `now\s+works?\b` is unqualified by design (C-5's real near-miss, *"AT28C parts should now work"*, had no object to anchor on). In v1.30 that pattern will fire on honest sentences like *"the leg now works in the native envs"* — and the checker's own docstring warns the wrong response is to narrow the pattern. Without D-16's window, authors will narrow it.
- **Missing arming in the v1.22 copy.** With `_HERE`-relative defaults and no arming, the gate is **RED from the moment it is authored until every closing artifact exists** — which conflicts with this project's practice of authoring gates early (v1.23 BASE-01…08 authored six gates before any firmware moved).
- **Env-var collision.** `FIRESTARTER_CLAIMSCAN_TARGETS` would be shared by **three** checkers. Assumption A3 records this as safe *"today"* because *"the two checkers live in different phase directories and never coexist in one process"* — and names the fix: *"suffix the name (e.g. `_V123`), not to reuse a single seam across two live scanners."* A third scanner makes suffixing mandatory.
- **Test-module basename collision.** Three files named `test_check_permitted_claims.py` in three non-package directories. Under pytest's default `prepend` import mode that is an "import file mismatch" collection error for anyone who ever runs pytest from `/workspaces`. (The app's own CI is unaffected — it runs from `firestarter_app/` — but the meta repo runs no pytest workflow at all, which is exactly how v1.23's C-3 RED went unseen.)
- **Archival orphaning.** Phase dirs get archived at close. A checker whose defaults name a sibling phase dir by a **string literal** breaks silently when either directory moves. This is the documented class *"Milestone close breaks its own record gates — archived sections orphan `lines=N` exemptions; `git rm REQUIREMENTS.md` trips fail-closed target lists."*

**The right claim-gate design for v1.30:**

1. **Fork from the v1.22 copy for its VOCABULARY, from the v1.23 copy for its MECHANICS.** Concretely: v1.22's eight AT28C/silicon patterns + v1.22's `REQUIRED_CAVEAT_PROSE` shape, retargeted (`"no AT28C silicon was tested"` remains exactly right and is already the milestone's ceiling sentence); plus v1.23's D-16 proximity window (token = `at28c|sdp|0x0d`), D-15 all-or-nothing arming, and hoisted never-vacuous guard.
2. **Add the milestone's own forbidden claims** — the ones the evidence ceiling actually forbids, which v1.22's set does not cover:
   - `lock inhibited the write` / `the lock held` (unqualified)
   - `proven behaviour` / `behaviourally verified` / `behaviorally verified`
   - `now provable` drifting to `now proven` — forbid `now proven` outright
   - `self-verifying` used without the word "emission" or the caveat in the window
   - `dev test proves` (unqualified)
   Cross-check the final list against REQUIREMENTS' Validation Ceiling section once written, the way v1.23 did (*"both sources agree on all eight"*).
3. **Resolve targets against the checker's OWN phase dir and put the checker in the phase that AUTHORS the artifacts** — i.e. the close phase. That is v1.22's shape and it was correct *for v1.22* precisely because author and host were the same phase. Do not repeat v1.23's cross-phase pre-authoring unless the arming + sibling-dirname coupling is re-derived from scratch, with a test.
4. **Two mandatory NEW test legs beyond the seven v1.22 already has**, both about the failure modes above:
   - `test_default_targets_resolve_inside_this_phase_directory` — asserts every `_DEFAULT_TARGETS` entry's resolved path has this module's own directory as its parent. This is the one assertion that makes a future naive copy fail loudly instead of passing against a stale sibling.
   - `test_default_target_basenames_are_this_milestones` — asserts every default target basename starts with this phase's number prefix. A copy carrying `130-*.md` names into a `13x-` phase goes red immediately.
5. **Suffix the env seam** (`FIRESTARTER_CLAIMSCAN_TARGETS_V130`) and **rename the test module** (`test_check_permitted_claims_v130.py`) to defuse both collisions.
6. **Carry v1.22's explicit non-claim verbatim**: a green run is *"the mechanizable half"* only, closed by this gate **plus** a blocking operator wording review. v1.22's D-16 review and v1.30's stated *"behind operator wording review"* for the gh#12 reply are the same instrument.
7. **Because the meta repo runs no pytest workflow**, the checker's own suite must be run as an explicit, recorded acceptance criterion in the phase (`pytest .planning/phases/13x-…/ -q`, output captured in the SUMMARY). v1.23's C-3 found this checker's suite *already RED* (`1 failed, 9 passed`) with nothing able to notice.

**Warning signs:**
- A `check_permitted_claims.py` appears in a v1.30 phase dir whose docstring still says "py32" or "PY32F071".
- The checker prints `PASS:` before any v1.30 closing artifact exists.
- The `PASS:` line names files with a `130-` prefix.
- `grep -c FIRESTARTER_CLAIMSCAN_TARGETS` across `.planning/` returns more than two distinct env-var names for three checkers.

**Where it bit before:**
v1.22 C-5 (the overclaim reached a **locked** decision D-14). v1.23 C-2 (`_HERE`-relative defaults → `UNARMED:` + exit 0, *"a green run that scanned nothing, on the milestone's only outward-facing overclaim gate"*). v1.23 C-3 (the checker's own suite was already RED and CI could not see it). Memory: *"`check_permitted_claims.py`'s `_HERE` resolves to the CHECKER's phase dir — cross-phase reuse scans nothing and exits 0; repoint `_DEFAULT_TARGETS`, never pass argv."*

**Phase to address:** the close phase (proposed **136**) authors and hosts it; the gate-hardening phase (**131**) may pre-author the **vocabulary list and the two new test legs** as long as the targets resolve locally.

---

### P-12 (HIGH): "Now provable" drifts into "now proven" in the four outward-facing artifacts

**What goes wrong:**
The milestone's honest claim is: *the lock's emission is provable, the plan derivation and read-back logic are provable, and the causal claim is reachable only from a community `dev test` report which does not gate the close.* Four artifacts will be written by someone who has just spent a milestone making the leg work, and the natural sentence is "the SDP lock is now verified" — because in every sense the author cares about, it is.

The four surfaces at risk, all outward-facing:
1. The **gh#12 reply** — and it must additionally state honestly that gh#12 asked for "enable/disable" and gets neither *by that name*; a rewording of the reporter's own ask, *"and should be stated as such"*.
2. The **app release notes** for the next beta cut.
3. The **milestone ledger / decision** artifacts.
4. The **`dev test` report text itself** — which goes to strangers on every run and is the surface no gate scans today.

Surface 4 is the one no existing mechanism covers: `check_permitted_claims.py` scans `.md` artifacts, not `diagnostic_report.py`'s rendered strings.

**Mechanical prevention:**
1. Add `firestarter_app/firestarter/diagnostic_report.py` (or a captured rendering of it) to the claim gate's target set — or better, add a **host-side** checker in `firestarter_app/tools/` scanning the report renderer's string literals against the same forbidden vocabulary, with a planted-violation fixture in the established house style. That gate lives in the app repo where CI actually runs it.
2. The positive-framing assertions from P-06 (`"cannot be read back"`, `"not a claim about the chip's actual state"`) applied to the leg's report rows.
3. The blocking operator wording review, as an explicit non-`<automated>` step. v1.30 already records the gh#12 reply as *"behind operator wording review"* — keep it there and do not let a plan's `<automated>` block draft it.

**Where it bit before:** v1.22 C-5 / D-14; v1.23's six-tier honesty ledger pairing every permitted claim with an explicit non-claim (18 corrections landed under a label-aware checker, 0 unlabeled of 60).

**Phase to address:** 133 (the report renderer's own strings + gate), 136 (the four artifacts).

---

# PART D — Gates that fail OPEN

### P-13 (CRITICAL, and already RED): `check_mypy_watermark.py` — reproduced locally this session

**What goes wrong — measured, not inferred.** Run in this devcontainer, 2026-08-03:

```
$ mypy firestarter/ tests/
pyproject.toml: [mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)

$ python3 tools/check_mypy_watermark.py
mypy errors: 1 (watermark: 35)
INFO: 1 errors — 34 below watermark. Lower watermark in pyproject.toml.
$ echo $?
0
```

The gate's own anti-bypass guard (`count_mypy_errors`, `tools/check_mypy_watermark.py:44-73`) is written correctly for the failure it anticipated — *"a broken type checker must fail the gate, never be mistaken for a clean tree"* — and is **defeated by the abort producing a parseable count**. `re.search(r"Found (\d+) errors?", output)` matches `Found 1 error`; `1 <= 35`; exit 0. Two independent tells were printed and ignored, and the gate then *invites you to lower the watermark* — which would bake the broken run's number in permanently.

`requires-python = ">=3.9"` and `python_version = "3.9"` are both correct for the package; the devcontainer's Python 3.12 is what makes them unsatisfiable locally. CI runs 3.11 (`ci.yml:36`) and is **RED with 69 errors against a watermark of 35**.

**Mechanical prevention (five parts; the last is the load-bearing one):**
1. **Fail on `errors prevented further checking`** anywhere in the output → `sys.exit(2)`.
2. **Fail on any line matching `^pyproject\.toml: \[mypy\]:`** — a config rejection is never a clean run.
3. **Invoke `[sys.executable, "-m", "mypy", ...]`, not bare `"mypy"`.** The bare form resolves to whatever is on `PATH` (`/home/vscode/.local/bin/mypy` here) with an unrelated interpreter and site-packages.
4. **Pin mypy** to a narrow range in the `[test]` extra (it is currently `mypy>=2.1.0`, unbounded) so the output format the regex depends on cannot drift.
5. **A canary floor, not just a ceiling.** Commit a tiny fixture module with a known, deliberate number of type errors and assert the run reports **at least** that many. An aborted or scope-collapsed run loses the canary's errors and the gate goes red. This is the only one of the five that catches an *unanticipated* abort mode — the other four each patch one known symptom. The paired planted-violation fixture discipline this repo already uses everywhere (`tests/fixtures/planted_*.py`) is exactly this idea.
6. **A paired pytest** (`tests/test_check_mypy_watermark.py` does not exist today) invoking the checker as a **subprocess** against planted mypy output, in the shape of `test_check_permitted_claims.py`'s seven legs: clean pass, exceeds-watermark, aborted-run, config-rejection, unparseable, and canary-missing.

**On the 69 errors themselves:** v1.23 measured its own net contribution at **zero** (69 → 72 → 69), so the debt is genuinely inherited. Two traps in discharging it:
- **Do not lower the watermark to make the gate green.** That is the fail-open move in a different costume — and `RETROSPECTIVE.md`/BASE-08's principle (*amending a ship gate so your own act clears it*) names it directly. Fix errors and **lower the watermark to the new true count** in the same commit, or raise it explicitly with a dated, reasoned comment.
- **Fix the gate before counting.** Any error count measured with the broken gate is meaningless. Order: harden → measure in a CI-equivalent env → fix → re-measure → set watermark.

**Warning signs:**
- `python3 tools/check_mypy_watermark.py` prints "N below watermark. Lower watermark in pyproject.toml." with N in single digits.
- The CI `ci` job is red on the mypy step but green locally.
- A commit lowers the watermark without a diff to any source file.

**Where it bit before:** v1.23 Phase 127 Plan 11 found it and, per operator instruction, **did not fix it** — carried as an open finding (`.planning/STATE.md:1049`). Memory: *"Devcontainer py3.12 masks app CI (py39/3.11) — mypy watermark gate is FAIL-OPEN locally (hid 69 errors)."*

**Phase to address:** **131**, first plan, before any other work — every later phase's green suite is otherwise unverified.

---

### P-14 (HIGH): The fail-open idioms present in `firestarter_app/` today, and which of them this milestone's own gates would inherit

Surveyed this session. The inventory:

| Idiom | Where | Status | Can v1.30's new gates inherit it? |
|---|---|---|---|
| **`_FW_ABSENT = not <one file>.exists()`** — a firmware *rename* reads as firmware *absence*, flipping legs PASS→SKIP at exit 0 | was in **seven** host test modules | **FIXED** in Phase 123 Plans 07/08 → `tests/fw_presence.py` keyed on the un-renameable `../firestarter/.git`, plus `MissingScanTargetError` making a missing target under a present repo a hard failure. Recurrence forbidden by `tools/check_no_exists_proxy.py` (an AST walk over module-level assignments, with `tests/fixtures/planted_no_exists_proxy.py`) | **No** — v1.30 touches no firmware. But `.planning/STATE.md:703` warns *"six modules shared it — worth confirming none survive"*: run `check_no_exists_proxy.py` as a cheap acceptance leg. |
| **A parseable-but-aborted subprocess count** | `tools/check_mypy_watermark.py` | **BROKEN** (P-13) | **Yes, directly** — any new checker that greps a tool's stdout for a number. The canary-floor rule generalises. |
| **Allow-list of function names, fail-closed only on ZERO matches** | `tools/check_devtest_orchestrator.py:138` `_HANDLER_FUNCTION_NAMES` | fail-open **against additions** | **Yes** (P-07) — and v1.30 adds functions to exactly the scanned handler. |
| **Explicit non-pattern default target lists** (never a glob, never a tree-walk, so `fixtures/` is unreachable) | `check_no_exists_proxy.py`, `check_devtest_orchestrator.py`, both `check_permitted_claims.py` | **CORRECT — copy this** | Yes, deliberately. |
| **Env seam read with `os.environ.get(...)` and NO default, precedence tested with `is not None`** so present-but-empty ⇒ zero targets, never a silent fallback | `FIRESTARTER_CLAIMSCAN_TARGETS`, `FIRESTARTER_DISP01_REPORT`, `FIRESTARTER_DEVTEST_SRC`, `FIRESTARTER_PROXY_LINT_TARGETS`, `FIRESTARTER_FW_ROOT` | **CORRECT — copy this** | Yes. |
| **Import-time binding** — `FW_ROOT`, `FW_REPO_PRESENT`, `requires_fw`, `_BOARD_CHOICES`, `channel.is_prerelease_build()`'s effect on option construction are all frozen at import/collection; `monkeypatch.setenv` runs **after** and has **no effect** | `tests/fw_presence.py:35-45` documents it explicitly (RESEARCH C-15) | correct-but-treacherous | **Yes** — any v1.30 test that tries to simulate the *stable* channel in-process will silently test the prerelease channel and pass. Must use a subprocess (P-17). |
| **`except Exception: pass` diagnostic swallow** | `chip_test.py:1036-1040` `_sample` | correct **for a sampler** | **Yes, hazardously** — it is a precedent an implementer will cite around the oracle (P-09 D6). |
| **Best-effort read-back swallow leaving a boolean verdict standing** | `chip_test.py:1147-1160` | correct **for a fingerprint** | **Yes, hazardously** (P-02, P-03c). |
| **`_diff_offsets` never raises; empty input ⇒ zero differences** | `chip_test.py:93-104` | correct **for a divergence metric** | **Yes, hazardously** (P-02). |
| **`${sysenv.VAR}` build-flag gating fails OPEN** | firmware side | documented, and `firestarter/channel.py`'s docstring cites it: *"A channel gate that can be flipped by an env var is not a gate — the firmware side already learned that `-D X=${sysenv.VAR}` fails OPEN and quietly ships the gated thing. **Nothing here reads the environment.**"* | **No, if 999.15 reuses `channel.py`.** Yes if it invents a new env-var-driven gate. `channel.py` is the correct pattern and fails **closed** on an unparseable version. |
| **A gate authored before its content is UNREACHABLE and nothing notices** | v1.23 general finding | class-level | **Yes** — v1.30 will pre-author gates. Every pre-authored gate needs a RED-preserving proof that it can *actually* fire on a planted violation, and its failure reasons must be *read*, not assumed. Memory: *"A pre-authored gate leg can be UNREACHABLE — RED proves nothing until seen to pass."* |
| **`test_skip_census.py`'s `ALLOWED_SKIP_REASONS`** | fails **closed** on any new skip reason; `test_census_child_run_is_live` prevents a collection regression from silencing it; `test_parser_recognises_a_real_skip` prevents a dead parser from making it vacuous | **CORRECT — a v1.30 ally** | Use it. Do not add an SDP entry casually. |

**Phase to address:** 131 owns the sweep (`check_no_exists_proxy.py` re-run, the derived `_HANDLER_FUNCTION_NAMES` subset test, mypy hardening); 133 owns not inheriting the three `chip_test.py` swallows.

---

# PART E — Deleting a published surface

### P-15 (HIGH): The syrupy snapshot fails the whole session — twice, for two different reasons

**What goes wrong:**
`tests/__snapshots__/test_characterization.ambr` line **141** contains, inside the `test_help_dev` snapshot (`# name: test_help_dev`, line 124):

```
    sdp                Enable or disable Software Data Protection (SDP) on...
```

Deleting the subcommand changes `firestarter dev --help` and reddens `test_help_dev` — expected, and easily fixed. The **second** failure is the one v1.23 hit and is not obvious:

**syrupy 5.5.3 fails the entire pytest session on UNUSED snapshots**, unless `--snapshot-warn-unused` is passed. Verified in syrupy's own source: `pytest_sessionfinish` does `session.exitstatus |= exitstatus | session.config._syrupy.finish()`, and `session.py:301`'s branch is `elif not self.update_snapshots and not self.warn_unused_snapshots:`. `firestarter_app`'s `addopts` is `"-ra -q"` — **no** `--snapshot-warn-unused`. So:

- If `test_help_dev` is renamed or parametrised — which the 999.15 channel split **requires**, into `test_help_dev[test_help_dev_stable]` / `[..._prerelease]`, exactly the shape `test_help_fw` already uses (`.ambr:168`, `:212`) — the old unnamed `test_help_dev` entry becomes **unused** and fails the session **even though every assertion passes**.
- `pytest --snapshot-update` deletes unused entries, but **regenerates every snapshot in the selection**, silently blessing any unrelated drift. Running it broadly to "fix the reds" is how a genuine regression in `test_help`, `test_info_known_chip` or `test_list` gets committed as the new truth.

**Mechanical prevention:**
1. **Scope the update** to the affected node ids only, then **review `git diff tests/__snapshots__/test_characterization.ambr` against a named expected shape** as an explicit acceptance criterion: *"the only changes are the removal of the `sdp` line from `test_help_dev` and the addition of two named `test_help_dev[...]` entries"*. Record `git diff --stat` in the SUMMARY. A diff-shape criterion is version-independent and does not rely on syrupy's node-scoping behaviour being what you think it is.
2. **Do the channel split and the deletion in a deliberate order**: delete first with a plain snapshot update (one-line diff), then split into two named snapshots (two-entry diff). Two small reviewable diffs beat one large one.
3. Copy `_run_fw_help_at_version` (`tests/test_characterization.py:242-286`) rather than reinventing it — it already solves the import-time channel binding *and* documents why `CliRunner` is wrong here (`CliRunner.isolation()` forces `click.formatting.FORCED_WIDTH = 80`, which wraps help text differently from a real subprocess's unforced 78). Generalise it to `_run_help_at_version(argv, version)`.

**Where it bit before:** v1.23 — *"the merge changed `fw --help` and reddened a snapshot, and the fix had to be channel-aware because `_BOARD_CHOICES` is import-time"*; Phase 127 Plan 04 took approved added scope to split `test_help_fw` into two named snapshots for exactly this reason.

**Phase to address:** the deletion phase (**132**) for the removal diff; the channel-gating phase (**135**) for the split.

---

### P-16 (HIGH): Deleting `tests/test_dev_sdp_cmd.py` deletes four honesty assertions that exist nowhere else

**What goes wrong:**
`tests/test_dev_sdp_cmd.py` (558 lines) is named for deletion. It contains, besides the gate-ordering cases the design note flags for repurposing, **four tests that are the only committed enforcement of the milestone's own honesty requirements**:

| Test | What it is the only enforcement of |
|---|---|
| `test_summary_line_carries_the_unreadable_state_caveat_on_both_directions` (`:395`) | that the caveat appears on **both** directions. Its docstring records *why* the host is the sole carrier: firmware's `0x5F` (`MSG_INFO_SDP_UNLOCK_DONE_US`) frame *"carries no honesty caveat where `0x61` (`MSG_INFO_SDP_LOCK_DONE_US`) does (F-120-03) — so the host summary line is the ONLY carrier of the caveat on the unlock direction."* |
| `test_summary_line_carries_no_duration_figure` (`:423`) | that no fabricated microsecond figure leaks into the host's own line |
| `test_no_fabricated_lock_state_boolean_in_the_report` (`:453`) | the three positive-framing assertions: `"was emitted"`, `"cannot be read back"`, `"not a claim about the chip's actual state"` |
| `test_firmware_too_old_is_reported_when_unknown_cmd_comes_back` (`:513`) | that an old firmware answering `0x0D`-unknown is *reported*, not silently absorbed. **Note:** *"Host cannot distinguish firmware b11 from b12"* — `_probe_port`'s `[\d.x]+` truncates the prerelease suffix, so an ack is the only detector. This is still true and the new leg needs it. |

Deleting the file with a `git rm` retires all four. A community member on b14/b15 firmware would then get the new leg with none of these guarantees, and no test would notice.

**Mechanical prevention:**
1. **`git mv`, don't `git rm`.** Move the file to `tests/test_dev_test_sdp_leg.py` in the same commit and retarget each case onto the new leg. The four honesty cases apply almost verbatim — the SUT changes from `dev sdp <chip> enable` to the leg's report rows.
2. **Order the leg BEFORE the deletion.** Deleting first opens a window in which the SDP capability has no test coverage at all and the four assertions exist nowhere. If the roadmap wants deletion early (to shrink 999.15's diff), do both in the **same phase**.
3. **An acceptance criterion asserting no net loss of assertions**: `git log --diff-filter=D --name-only` for the phase must show the old file only if the new file exists in the same commit, and the four assertion strings (`"cannot be read back"`, `"not a claim about the chip's actual state"`, `"was emitted"`, plus the duration-regex) must each still be grep-findable in `tests/`. Four greps, mechanical.

**Where it bit before:** the general class is memory-recorded: *"'Empty git diff' criteria break on later `#if` guards — scope to assertions-unchanged, or name blob SHAs."* Same lesson: assert the *assertions*, not the file.

**Phase to address:** 132/133 jointly (recommend one phase).

---

### P-17 (MEDIUM-HIGH): Every other trace a deleted subcommand leaves

Enumerated. Grepped this session; the surprising result is how *little* is in the app repo and how much is outside it.

| # | Trace | Location | Breaks how | Prevention |
|---|---|---|---|---|
| 1 | **`test_help_dev` snapshot** | `tests/__snapshots__/test_characterization.ambr:141` | P-15 | scoped update + diff review |
| 2 | **Unused-snapshot session failure** | syrupy default | P-15 | as above |
| 3 | **`tests/test_dev_sdp_cmd.py`** | 558 lines, 4 honesty tests | P-16 | `git mv` |
| 4 | **`COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` and their `COMMAND_NAMES` entries** | `constants.py:72-73`, dereferenced at `eprom_operations.py:301` and `:377` | **a missing `COMMAND_NAMES` entry is a `KeyError` at operation setup, not a cosmetic gap.** An over-eager "remove the SDP constants" cleanup breaks `write`'s auto-unlock and `--sdp-relock` too | a test that dereferences `COMMAND_NAMES[COMMAND_SDP_LOCK]` and `[COMMAND_SDP_UNLOCK]` and asserts non-empty. Trivial and permanent. |
| 5 | **`sdp_capability.py` in full** | now serves three consumers: `write`'s D-04 auto-set, the new leg, `--sdp-relock` | deleting or narrowing it breaks all three | the count/parity gate from P-10 |
| 6 | **`shell_complete=_complete_eprom` registrations** | `cli_handlers.py:2194` | a user's cached shell completion still offers `dev sdp` after upgrade | not fixable host-side; mention in release notes |
| 7 | **The gh#12 reply** (`122-GH12-COMMENT.md:15`), **published 2026-07-30** | GitHub, `henols/firestarter_prom` | a one-day-old public instruction becomes wrong; and gh#12's ask is *reworded*, not answered | the owed follow-up, **behind operator wording review**, stating the substitution honestly and not letting "now provable" become "now proven" (P-12) |
| 8 | **b14 app release notes** (`122-RELEASE-NOTES-app.md:12,22`), same date | GitHub release | names a command that no longer exists in the next beta | a "Removed" section in the next release notes naming the replacement paths explicitly |
| 9 | **PyPI `--pre` installs of `3.0.0b14`/`3.0.0b15`** | live | `firestarter dev sdp` starts erroring for anyone who upgrades | Click's own "No such command" is adequate *if* the release notes carry the mapping. Consider a one-release deprecation shim that errors with the replacement instruction — but note it would then need 999.15 channel classification, which is exactly the diff the deletion is meant to shrink. **Recommend: clean deletion + release-notes mapping.** |
| 10 | **`.planning/` record** — `PROJECT.md`, `STATE.md`, `MILESTONES.md`, the v1.22 phase artifacts, `ROADMAP.md` | meta repo | archived/historical text legitimately describes a shipped command. **Do not sweep it.** v1.23's C-7 found that a naive sweep *"would have deleted accurate history"* | use the established `<!-- recordscan:history reason: … -->` labelling for anything a live-claim scanner flags; correct only *live* forward-looking statements |
| 11 | **The stale `--sdp-relock` deferral label** | `.planning/STATE.md:532` and `.planning/PROJECT.md:705` read **"v1.23+"**, written before v1.23 became PY32F071 Integration. (The design note's own `STATE.md:154` / `PROJECT.md:671` citations are themselves stale — the live lines are 532/705) | the flag currently has no home; a reader following the label lands on a shipped, unrelated milestone | fix both rows when the stub is scoped, as an explicit task, *"not silently left to be discovered"* |
| 12 | **No app-repo `.md` mentions it** | verified: `grep -rn "dev sdp" --include=*.md firestarter_app/` → **zero hits**; `README.md` mentions only `dev test` (`:131-133`) | nothing to fix | confirm with the same grep as an acceptance leg |

**Phase to address:** 132 (traces 1–6, 12), 135 (trace 9's interaction), 136 (traces 7, 8, 10, 11).

---

# PART F — Test-suite hazards specific to this repo

### P-18 (HIGH): The devcontainer cannot see three whole classes of defect this milestone can ship

Three independent divergences, all live:

**(a) Python 3.12 local vs 3.11 CI vs a 3.9 floor.** This is precisely what made the mypy gate fail open (P-13). It also means: any `from __future__` / typing-syntax / stdlib-behaviour assumption that works at 3.12 may fail at 3.9 (`requires-python = ">=3.9"`; `ruff target-version = "py39"`; `mypy python_version = "3.9"`). ruff *is* CI-scoped correctly today, but must be **run CI-scoped locally** (`ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`) — not on a wider or narrower path set.

**(b) The sibling-repo layout.** This devcontainer **has** `../firestarter/`; standalone CI does **not**. `.planning/STATE.md:688-697`:

> *"⚠ Before any push to a sub-repo `beta`, point the sibling checkout root at an empty directory first. This devcontainer *has* the sibling layout standalone CI lacks, which is exactly why three CI-only sibling-checkout test defects fired simultaneously on the real b15 push and were invisible locally."*

Two out-of-plan fixes landed directly on `beta` during that hand-off (`firestarter_app` `5934a54` — which is the current fork base `16a313a`'s parent), and **one of them softened a Phase-129-authored hard assert (`test_present_root_with_missing_target_raises_not_skips`) to a skip — a defect-class change**, recorded as worth revisiting.

**(c) A live board on `/dev/ttyACM*` beats the `comports=[]` patch.** `test_no_programmer_found_read` / `_erase` (`tests/test_characterization.py:478`, `:518`) *have already been hardened*: they now patch `SerialCommunicator._list_potential_ports` (the real enumeration seam, D-19) **as well as** `comports`, and assert `mock_serial.assert_not_called()`. Any **new** test the SDP leg adds that touches port discovery must do the same, or it goes red on the operator's bench and green in CI — or worse, green in both while having silently opened a real port.

**Mechanical prevention:**
1. **A CI-equivalent local run recipe, executed and recorded, before any push to `beta`:**
   ```
   FIRESTARTER_FW_ROOT=$(mktemp -d) python3 -m pytest tests/ -q     # (b) empty sibling root
   python3 -m pytest tests/ -q                                      # with the sibling present
   ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/
   python3 tools/check_mypy_watermark.py                            # after P-13's fix
   ```
   `FIRESTARTER_FW_ROOT` is the **one** seam `fw_presence.py` exposes for exactly this (`:80`), and it is read at **module scope** — so it must be set in the **environment of the pytest process**, never monkeypatched.
2. **Also detach the physical board** (or run with no `/dev/ttyACM*`) for one of the two runs, and record both.
3. **Prefer a 3.9-or-3.11 verification for anything type-related.** If a matching interpreter is unavailable locally, say so and defer the claim to a CI run URL — the same discipline v1.23 D-07 imposed on ARM sizes (*"a local build supports delta / byte-identity claims only — never an absolute size"*).
4. **Revisit the softened assert** (`test_present_root_with_missing_target_raises_not_skips`) as a named item: it was a Phase-129 hard assert downgraded to a skip under time pressure, and it is currently the fork base. Either restore the hard assert with a correct standalone-checkout guard, or record the downgrade deliberately.
5. **The still-owed `81fa53c` carry.** `.planning/STATE.md:534` and `:684-686`: an app CI fix exists on `beta` **only** and *"must be reintroduced at the next merge toward `main`"* — it adds `skipif` guards to `test_check_is_memory_cmd_no_ifdef.py` and `test_check_no_log_in_sdp_window.py`'s clean-source legs, which hard-fail in a standalone checkout. **`main` has still never been merged in any of the three repos**, so this stays latent — but v1.30 touches `check_no_log_in_sdp_window.py`'s neighbourhood and should not make it worse.

**Where it bit before:** the b15 push (three simultaneous CI-only failures); Phase 122's `122-CUT.md` §8; memory: *"Devcontainer sibling layout masks CI-only test defects — point the sibling root at an empty dir BEFORE any beta push."*

**Phase to address:** 131 authors the recipe as a reusable acceptance leg; every phase runs it; the cut phase (136) runs it before any push.

---

### P-19 (MEDIUM): The stable channel surface is unreachable in any local run

**What goes wrong:**
`channel.is_prerelease_build()` (`firestarter/channel.py:36-57`) derives the channel from the package's own `__version__`, and *"dev versions (`2.0.7_dev`) parse as pre-releases and therefore keep gated features enabled while working from a checkout."* So **every local run, and every in-process test, sees the prerelease surface.** 999.15's whole deliverable is the *stable* surface (`dev read` + `dev test` only), and it cannot be observed locally by default.

Compounding it: option construction and `_BOARD_CHOICES`-style choices bind at **import time**, so `monkeypatch.setattr("firestarter.__version__", "3.0.0")` inside a test that has already imported `cli_handlers` does nothing — and *passes*.

**Mechanical prevention:**
1. **Simulate the channel in a subprocess**, patching `firestarter.__version__` *before* `cli_handlers` is imported. `_run_fw_help_at_version` (`test_characterization.py:242`) and `tests/test_py32_channel_gating.py`'s D-07 discipline both already do this; generalise, don't reinvent.
2. **Both channels pinned against their OWN named snapshot**, per `test_help_fw`'s rationale: *"if `--board`'s real choices ever drift from what a channel should expose, one of these two assertions goes red — neither is derived from the other."* Apply to `dev --help`.
3. **Positive AND negative membership assertions**, not just snapshots — e.g. `assert "sdp" not in stable and "sdp" not in prerelease` (post-deletion), `assert "test" in stable`, `assert "read" in stable`, `assert "reg" not in stable`. A snapshot alone tells you the text changed; these tell you *what* the channel exposes.
4. **Reuse `channel.py`. Do not invent an env-var gate.** Its docstring is the project's own recorded lesson: *"A channel gate that can be flipped by an env var is not a gate."* It fails **closed** on an unparseable version.

**Where it bit before:** memory: *"gh#8 dev-tools gating: the CHANNEL is the gate — stable keeps `dev read`+`dev test`; `${sysenv.VAR}` fails OPEN."* And v1.23's `test_help_fw` split.

**Phase to address:** 135, with the harness authored in 131 or 132 (whichever first needs a channel-aware help assertion).

---

# PART G — Leaving a chip locked

### P-20 (CRITICAL, safety): An abort between lock and unlock ships a locked part back to a community member

**What goes wrong:**
`run_plan` (`chip_test.py:757-802`) is a **flat `for` loop over `plan.steps`** with per-step `try/except` and **no `try/finally` and no cleanup phase**. Its per-step handler catches `EpromOperationError`, `ChipNotImplementedError`, `ChipNotFoundError` — not `KeyboardInterrupt`, not `SystemExit`, not a `serial` transport exception class outside that set. So:

- **Ctrl-C** between step 2 (`sdp_lock`) and step 4 (`sdp_unlock`) → the loop unwinds, `dev test` exits, the part stays locked.
- **A cable yank / brownout** → an unhandled transport exception propagates the same way.
- **The destructive gate.** If `sdp_lock` is placed in `_DESTRUCTIVE_OPS` (it must be — it mutates the part) but the id step is *later* re-run or the gate closes *mid-plan*, the write steps skip while the lock does not, or vice versa. Worse and more likely: **if `sdp_unlock` is placed in `_DESTRUCTIVE_OPS`, a gate that closes after the lock will SKIP the unlock** — the gate designed to protect the chip becomes the mechanism that leaves it locked.
- **A `sdp_unlock` emission failure** at step 4 → `BAD` (exit 1), which is honest, but the part is locked and the report must say so in recovery terms, not just "BAD".

Recovery genuinely exists — firmware auto-unlocks at the start of **every** protocol-`0x0D` write (`eeprom28c_write_init`; host side `eprom_operations.py:1637`) — so a plain `firestarter write` recovers the part. But: **`0x0D` has no erase operation at all.** The word "erase" in a recovery instruction is not merely imprecise, it is *actively wrong advice* that sends a user looking for a command that does not exist for their chip and cannot exist.

**Mechanical prevention:**
1. **`sdp_lock` in `_DESTRUCTIVE_OPS`; `sdp_unlock` EXEMPT from the destructive gate.** The gate's purpose is "don't mutate a chip you can't identify". A cleanup unlock on a possibly-misidentified chip is the lesser harm than leaving a possibly-locked chip — and if the lock never ran, the unlock is a no-op emission. Encode the asymmetry explicitly with a comment and a test: *closed gate ⇒ `sdp_lock` SKIPPED and `sdp_unlock` not attempted (because nothing was locked); lock ran then gate closed ⇒ `sdp_unlock` STILL attempted.*
2. **A `try/finally` around the lock→unlock window**, wide enough to catch `BaseException`, whose `finally` attempts `sdp_unlock` once and records the attempt as a `StepResult` before re-raising. This is a deliberate, narrow deviation from `run_plan`'s flat-loop shape and must be documented as such.
3. **Baseline-gate the whole leg.** If step 1 (baseline write + verify) is not `OK`, steps 2–4 must **not run at all** — `SKIPPED` with reason *"baseline not established; the part was not locked"*. Locking a chip whose write path is already failing has zero oracle value and maximal harm. **This is not hypothetical: gh#20 (AT28C256 `dev test` FAIL, reported 2026-07-30) is still open** — the first community `dev test` report on an SDP-capable `0x0D` part is a failure, and v1.30 is about to add a lock to that same run.
4. **Report wording, asserted by test:**
   - On a completed run: *"the part was unlocked before this run ended"*.
   - On an aborted/failed-unlock run: an explicit recovery line using the word **"rewrite"**: *"this part may still be SDP-locked. Recover it by running `firestarter write <chip> <file>` — the firmware unlocks automatically at the start of every write. There is no erase operation for this chip family."*
   - Test both strings. A `"erase"`-forbidding grep over the leg's recovery strings is three lines and permanent.
5. **What host-side cleanup can honestly promise:** *"an unlock sequence was emitted"* — nothing more. Protection state is not readable on this family (Phase 117 D-05, Phase 119 D-12), so the report **cannot** say "the part is unlocked". It can say: the unlock was emitted; the emission returned OK; and a plain `write` will unlock it again regardless. Do not let the cleanup line become a state claim (P-06).
6. **Also state the endurance cost.** The leg adds three write passes to a run that already writes twice. `_ALWAYS_WRITES_NOTICE` must reflect the true count (P-08).

**Warning signs:**
- No `finally` anywhere in the leg.
- `sdp_unlock` appears in `_DESTRUCTIVE_OPS`.
- The recovery string contains "erase".
- A test kills the run mid-plan and asserts nothing about the unlock.
- Steps 2–4 run unconditionally after step 1's verdict.

**Where it bit before:** design-note Trap 3 states it. Related in-repo precedent for "the gate becomes the harm": Phase 119 LOCK-04's *"generic op-layer NULL-main guard, not the harmful `default:` arm"* — the same reasoning that a refusal must fail in the safe direction, chosen deliberately rather than inherited.

**Phase to address:** 133, as a named safety criterion.

---

# PART H — The removal-safety dependency

### P-21 (MEDIUM, but high half-life): "Removal is safe because auto-unlock is default-on" decays into an unfindable sentence

**What goes wrong:**
The deletion of the standalone unlock is safe **only** because firmware auto-unlocks on every `0x0D` write. If that default is ever revisited — made opt-in, gated, or removed — the deletion becomes reckless retroactively: there would then be **no** way for a user to recover an SDP-locked AT28C, and the standalone command that used to provide one is gone. The design note says *"record the dependency"*; PROJECT.md repeats it. **A sentence in a note is not a mechanism.** It will not be found by whoever changes the auto-unlock default two milestones from now, because they will be reading `eprom_operations.py`, not v1.30's design note.

**Mechanical prevention — put the tripwire where the change will happen, not where the decision was made.** Four layers, cheapest first:

1. **A comment at the change site.** In `eprom_operations.py` at the auto-unlock default (and at `FLAG_SKIP_SDP_UNLOCK`'s definition in `constants.py`), a block comment naming v1.30 and the dependency: *"the standalone `dev sdp <chip> disable` was DELETED in v1.30 because this unlock is unconditional. Changing this default removes the only recovery path for an SDP-locked part and must re-open that decision."* A developer changing the default reads this line by construction.
2. **A committed test that fails when the default changes.** `tests/test_write_skip_sdp_unlock.py` already exists and covers `--skip-sdp-unlock`; add a test named for the *dependency*, e.g. `test_auto_unlock_is_default_on_because_dev_sdp_was_deleted`, asserting that a `0x0D` write without `FLAG_SKIP_SDP_UNLOCK` set carries the unlock. Its **name and docstring** are the record. A test that fails and whose failure message explains the coupled decision is the only form of documentation that reliably gets read.
3. **A ledger row pairing the claim with its condition.** v1.23's six-tier honesty ledger paired every permitted claim with its explicit non-claim; do the same here: *permitted claim — "no capability is lost by deleting `dev sdp`"; condition — "auto-unlock is default-on"; if the condition fails, the claim fails."*
4. **An explicit `STATE.md` "coupled decisions" entry**, not merely a deferred item — deferred items get *acknowledged* (six consecutive closes for the standing 14), whereas a coupled-decision entry naming the exact source file is actionable. And a `todos` entry is not enough: 13 are already pending.

Layers 1 and 2 are the ones that survive; 3 and 4 serve the reader who is already in `.planning/`.

**Warning signs:**
- The dependency exists only in `.planning/notes/` and `PROJECT.md`.
- No test names it.
- No comment at `eprom_operations.py:1637` mentions it.

**Where it bit before:** the class is well documented here — `RETROSPECTIVE.md:409`: *"'Accepted tech debt' for a safety artifact deserves a tracked follow-up, not just a note. The hollow GATE-03 detector is safe today only because the host guard exists; if the host guard ever changes, the hollow gate won't catch it."* Identical structure, identical remedy.

**Phase to address:** 132 (comment + test land with the deletion); 136 (ledger + STATE row).

---

# PART I — Remaining pitfalls

### P-22 (MEDIUM): `--sdp-relock`'s skip-on-verify-failure is itself a false-green shape

**What goes wrong:**
Polarity is decided (operator, 2026-08-03): **on verify failure the relock is SKIPPED and the skip is reported loudly.** The hazard is the word "loudly". A skip that only appears in a log line at `INFO` is not loud; the user asked to protect a part and it is unprotected, and they will assume otherwise. Worse: because protection state cannot be read back, **there is no way for them to discover the part is unprotected** — the failure is permanently invisible on the hardware.

The symmetric hazard: relocking anyway would protect a bad image behind a lock that cannot be read back and can only be cleared by another write. That is why the decision is right; the implementation is what can betray it.

**Mechanical prevention:**
1. **A non-zero exit code**, or at minimum a `WARNING`-level message plus an explicit final line. `write` returning 0 after silently skipping the user's requested relock is the false green. Recommend: the write's own success drives the exit code, and the skipped relock adds a distinguishable non-zero (or a mandatory final `WARNING:` line asserted by test).
2. **The skip message must state the state the part is in** and how to retry: *"the write did not verify, so `--sdp-relock` was NOT applied — this part is UNPROTECTED. Fix the image or the contact and re-run with `--sdp-relock`."*
3. **Three committed tests**: verify-OK ⇒ relock emitted; verify-FAIL ⇒ relock **not** emitted (`operator.sdp_lock.assert_not_called()` — the SAFE-04 idiom) **and** the warning present **and** the exit code non-zero; flag absent ⇒ relock never emitted.
4. **Refuse `--sdp-relock` up front on a REFUSE-list chip**, before the port opens, with `sdp_capability()`'s own reason — the same gate-ordering discipline `test_dev_sdp_cmd.py:151-260` proves for `dev sdp` (four ordered gates, each refusing before the confirm and before any port is opened). Those gate-ordering cases are exactly what the design note means by *"repurpose the gate-ordering cases … where they still apply"* — they apply here, to `write --sdp-relock`, more than to the `dev test` leg.

**Also fix the stale label** (`STATE.md:532`, `PROJECT.md:705` read "v1.23+") as an explicit task, not a discovery.

**Phase to address:** the `--sdp-relock` phase (proposed **134**), inheriting 132's repurposed gate-ordering tests.

---

### P-23 (MEDIUM): New ops must be registered in more places than the code tells you

**What goes wrong:**
Adding ops to `chip_test.py`'s vocabulary touches a set of registries that is *partly* self-enforcing and partly not:

| Registry | Fails closed on omission? |
|---|---|
| `_DESTRUCTIVE_OPS` (`:636`) | **No** — an omitted write-shaped op writes to a misidentified chip ungated. The comment says so: *"a write-shaped op absent from this frozenset would write to a misidentified chip ungated by the chip-ID mismatch check, which is a critical-severity correctness bug, not a cosmetic omission."* |
| `_MULTI_RUN_OPS` (`:657`) | **Yes** — `BAD` with an explicit refusal reason. But see P-03: registering here is the trap. |
| `_dispatch_step`'s arms (`:903-948`) | **Yes** — the terminal `return StepResult(verdict=VERDICT_BAD, …)` refuses fail-closed |
| `derive_plan`'s step construction | **No** — an op simply never appears |
| `_RAN_VERDICTS` / `count_applicable` M | **No** — silently excluded from the coverage ratio (P-04 R7) |
| `dedup_fingerprint` hash inputs | **No** — the design note says consumers *"pick them up without learning a new field"*, which is true for reading `StepResult.op` but means the fingerprint's meaning silently changes |
| `diagnostic_report.py` renderer | **No** — an unrendered op is invisible in the report |
| `tools/parse_devtest_issue.py` | **No** — a new op in a filed issue may not parse |
| `_ALWAYS_WRITES_NOTICE` | **No** (P-08) |
| `check_devtest_orchestrator.py`'s allow-list | **No** for new *handler* helpers (P-07) |

**Mechanical prevention:** a single **op-registration parity test** that, for every op string in the module's `OP_*` constants, asserts membership-or-explicit-exemption in each registry above, with the exemptions listed and commented. One test, ten assertions, and it converts eight fail-open registries into one fail-closed gate. The house already has the shape (`test_revision_constants_parity.py`, `test_sdp_table_parity.py`, `test_dispatch_mirror.py`).

**Where it bit before:** Phase 121 Plan 06 added `OP_WRITE_PARTIAL` and had to add it to **both** frozensets, proven by a deliberate-break test (121-06 Task 3) — establishing the pattern but not generalising it.

**Phase to address:** 133 (the parity test lands with the new ops).

---

### P-24 (MEDIUM): Requirements get marked Complete before all their plans land

**What goes wrong:**
A documented, repeated executor behaviour in this project: *"Executors prematurely mark multi-plan reqs Complete — 4× in P116; name allowed IDs when dispatching."* This milestone has requirement clusters that will span plans (the leg's four steps; the mypy hardening; the channel split), so it is squarely in scope.

**Mechanical prevention:** name the exact requirement IDs each plan is permitted to mark Complete, in the dispatch prompt. Verify against the requirements file at phase verification, not at plan close.

**Phase to address:** every phase; a dispatch-time discipline.

---

### P-25 (LOW-MEDIUM): Planning-tool hazards that have bitten this project at exactly this point in the cycle

Not code pitfalls, but they cost real time in v1.22 and v1.23 and this milestone will hit the same steps:

| Hazard | Prevention |
|---|---|
| **`/gsd-new-milestone` step 6 `phases.clear` is DESTRUCTIVE** — hard-deletes 50+ phase dirs | skip it |
| **`gsd-tools query commit` can switch branches** — an unanchored `##…vX.Y` regex scrapes ROADMAP prose | `git rev-parse --abbrev-ref HEAD` after every `gsd-tools query commit`; `git diff` STATE.md after every state write |
| **`phase.complete` can CORRUPT frontmatter**, and jumps to (close) when the next phase has no dir | diff, don't infer; check the first `[ ]` checkbox |
| **`--auto`/`--chain` AUTO-APPROVES human-verify gates**; `autonomous: false` is not self-protecting | this milestone has an operator-wording-review gate (gh#12) and a bench-free evidence ceiling — do not run the close under `--auto` |
| **Tag pushes fire zero CI, but local `beta` lags origin**; a `beta` merge+push at close **auto-fires CI → a spurious new beta** (fired twice at v1.21) | ff-only to `origin/beta` **before** tagging; expect the CI fire and plan for it |
| **Milestone close breaks its own record gates** — archived sections orphan `lines=N` exemptions; `git rm REQUIREMENTS.md` trips fail-closed target lists | expect it; P-11's target-resolution tests are the local instance |

**Phase to address:** 136 and the close procedure.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|---|---|---|---|
| Reuse `generate_pattern` for both A and B | zero new code; looks idiomatic | **the milestone's only deliverable becomes a tautology** | **Never** |
| Register the inhibited write in `_MULTI_RUN_OPS` | the fail-closed instruction is satisfied; multi-run machinery for free | write-boolean oracle + double write + swallowed read-back (P-03) | **Never** |
| Compare with `_diff_offsets`/`==` and no length guard | one line; reuses the mandated primitive | empty read-back reads as perfect equality (P-02) | **Never** |
| Downgrade an unexpected write success to `SKIPPED`/`NA` | keeps `dev test` green for users | inverts the leg's entire purpose (P-09) | **Never** |
| Lower the mypy watermark to make CI green | `ci` job green today | bakes 69 unchecked errors in permanently; the fail-open move BASE-08 exists to prevent | **Never** — fix errors and lower to the true count in the same commit |
| Skip the SDP oracle when the lock emission fails | fewer moving parts | hides whether the write then succeeded (P-09 D3) | **Never** — run it and report both |
| `git rm tests/test_dev_sdp_cmd.py` | one clean commit | retires 4 honesty assertions with no replacement (P-16) | **Never** — `git mv` |
| Copy `check_permitted_claims.py` verbatim | a claim gate "for free" | a confident `PASS:` scanning v1.23's artifacts (P-11) | **Never** |
| A deprecation shim for `dev sdp` | kindest to b14/b15 `--pre` users | re-adds a subcommand 999.15 must classify — the exact diff the deletion shrinks | Only if 999.15 lands first and classifies it; otherwise clean deletion + release-notes mapping |
| Defer the causal claim to a community report | honest, and the only option | the milestone closes with its central claim unproven and **no** gate forcing anyone to say so | **Acceptable and correct** — this is the evidence ceiling. It is acceptable **only** with P-11's claim gate and an explicit ledger non-claim. |
| Rely on the report's `N of M` banner to surface a non-running oracle | free | `NA` steps are excluded from *both* N and M, so the ratio stays perfect (P-04 R7) | Never as the only signal |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|---|---|---|
| **PyPI `--pre` (b14/b15 carry `dev sdp`)** | delete silently; let users discover Click's "No such command" | release-notes "Removed" section mapping `dev sdp disable` → `write` (automatic) and `dev sdp enable` → `write --sdp-relock`; deletion is cheap now and *"strictly more expensive every week it waits"* |
| **GitHub `henols/firestarter_prom` (gh#12)** | reply claiming the ask was delivered | state the substitution honestly: gh#12 asked for enable/disable and gets neither *by that name*; a rewording of the reporter's own ask. Behind operator wording review. **Issue tracking is centralized in `henols/firestarter_prom`** — `dev test --submit` has misfiled into the app repo before and b11 still does |
| **`gh` CLI for the follow-up** | `gh issue create --label` with a non-existent label; assume write access | pre-existing labels only; assert the negative argv in a test |
| **Community `dev test` reports (the ONLY causal-evidence path)** | assume the report will arrive and gate the close on it | **it does not gate the close, by design.** Make sure the report *carries the evidence*: the SDP oracle's pre-write hash, read-back hash, and `HELD/NOT-HELD/NOT-RUN` state must be in `report.to_dict()`, or the one report that could settle `0x0D` arrives unable to |
| **`tools/parse_devtest_issue.py`** | new op strings unparsed in a filed issue | extend the parser and its golden fixtures in the same phase as the new ops |
| **Firmware (b14/b15) — NOT touched** | assume the host can tell b11 from b12 by version | it cannot: `_probe_port`'s `[\d.x]+` truncates the prerelease suffix. Detect capability by an **ack**, which is what `test_firmware_too_old_is_reported_when_unknown_cmd_comes_back` already does |
| **`beta` branch CI** | push and hope | the app b15 cut was gated on a full green `pytest tests/` plus two codegen gates, all blocking, all before the version bump. Run P-18's recipe first |

---

## Scale / Robustness Traps

Not user-scale — chip-scale and run-scale.

| Trap | Symptoms | Prevention | When it breaks |
|---|---|---|---|
| **Write-pass inflation** | `dev test` on an AT28C256 goes from 2 full-device write passes to 5–8 | make the SDP leg's write region the same bounded region the plan already chose (`step.write_region`), not a second full-device pass; state the true count in `_ALWAYS_WRITES_NOTICE` | immediately, on every ALLOW chip |
| **Run-time inflation on a community member's bench** | a `dev test` that took ~1 min takes several | as above; and `runs == 1` for the inhibited write (P-03b) halves the added cost | immediately |
| **EEPROM endurance** | not a practical limit (`0x0D` parts are rated ≥10⁴ cycles) but the *notice* must be honest | notice content assertion (P-08) | never practically; the honesty matters regardless |
| **43 ALLOW chips × 4 new steps in `derive_plan`** | plan derivation is pure and cheap; no risk | — | — |
| **`test_skip_census.py`'s full-suite subprocess (~40–50 s, `lru_cache`d)** | suite wall-clock grows as the milestone adds tests | it is already cached to one child run per session; do not add a second census-style module | if a second full-suite-in-subprocess test is added |

---

## Hardware-Safety Mistakes

| Mistake | Risk | Prevention |
|---|---|---|
| Locking a part whose baseline write never worked | a locked chip returned to a stranger with no oracle gained. **gh#20 proves this is live** | baseline-gate steps 2–4 (P-20.3) |
| `sdp_unlock` inside `_DESTRUCTIVE_OPS` | the chip-ID gate becomes the mechanism that leaves the part locked | exempt unlock; assert the asymmetry (P-20.1) |
| No `finally` around the lock→unlock window | Ctrl-C / cable yank / brownout ships a locked part | `try/finally` catching `BaseException`, one unlock attempt, recorded (P-20.2) |
| Recovery advice saying "erase" | actively wrong — `0x0D` has **no erase operation at all**; sends the user after a command that cannot exist | the word is **"rewrite"**; forbid "erase" in the leg's recovery strings by grep-gate (P-20.4) |
| A new write-shaped op omitted from `_DESTRUCTIVE_OPS` | writes to a **misidentified** chip, ungated by the chip-ID check | op-registration parity test (P-23) |
| `dev test` opening a port outside the orchestrator (SAFE-02) | the orchestrator-only contract broken invisibly | keep logic in `chip_test.py` (scanned in full); derived `_HANDLER_FUNCTION_NAMES` subset test (P-07) |
| A fabricated `locked: true` in the JSON artifact | a downstream consumer treats an emission as a state | no such key; assert its absence (P-06.3) |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---|---|---|
| `sdp_lock \| OK` in a **Verdict** column | reader concludes the chip is locked | non-empty emission-only `reason` on success, rendered (P-06) |
| An oracle that did not run, absorbed as `NA` at exit 0 | a "PASS" report proving nothing; the community-validation channel poisoned | a named, always-present report field: `HELD / NOT-HELD / NOT-RUN(reason)` (P-04.1) |
| `--sdp-relock` silently skipped on verify failure | user believes a part is protected; **cannot check, ever** | non-zero exit or mandatory `WARNING:` final line naming the state and the retry (P-22) |
| An understated always-writes notice | consent given on false information, before a part is sacrificed | notice content assertion (P-08) |
| A locked part with no recovery line | a stranger with a part that appears bricked | the "rewrite" recovery line, asserted (P-20.4) |
| `dev sdp` vanishing with no mapping | a b14/b15 `--pre` user's script breaks with "No such command" | release-notes "Removed" section + gh#12 follow-up (P-17.7/8/9) |

---

## "Looks Done But Isn't" Checklist

- [ ] **The SDP oracle:** patterns A and B asserted to differ at **every** byte, and neither equals blank or all-zero — verify a test exists that would fail if `generate_pattern` were used for both (P-01)
- [ ] **The SDP oracle:** a length guard precedes every comparison; `b""`, short, all-0xFF and all-0x00 read-backs each have a fixture asserting `BAD` (P-02)
- [ ] **The SDP oracle:** the inhibited-write op is **not** in `_MULTI_RUN_OPS`; `run_count == 1`; verdict provably driven by read-back, proven by BOTH directions (write-True+readback-B ⇒ BAD, write-False+readback-A ⇒ OK) (P-03)
- [ ] **Inverted sensitivity:** a test exists in which the inhibited write **succeeds** and asserts `VERDICT_BAD` + `exit_code == 1`. This is the milestone's single most important test (P-09)
- [ ] **Inverted sensitivity:** the oracle function contains no `VERDICT_NA`, `VERDICT_SKIPPED`, `VERDICT_MARGINAL`, or bare `except` (P-09.4)
- [ ] **Baseline:** a fixture whose chip already holds pattern A and whose write is a no-op reports `BAD`; the pre-write read hash is in the JSON artifact (P-05)
- [ ] **Exit-code laundering:** a test per route R1–R6, each asserting `sdp_lock.assert_not_called()` **and** a visible `NOT-RUN` reason (P-04)
- [ ] **Coverage banner:** an ALLOW-chip `NA`/`SKIPPED` oracle **drops** N/M and fires the banner (P-04 R7)
- [ ] **Safety:** `sdp_lock` ∈ `_DESTRUCTIVE_OPS`; `sdp_unlock` exempt; `try/finally` over the window; steps 2–4 gated on step 1 being OK; recovery says "rewrite" not "erase" — five separate checks (P-20)
- [ ] **Honesty:** the four `test_dev_sdp_cmd.py` honesty assertions are grep-findable in `tests/` after the deletion commit (P-16.3)
- [ ] **Deletion:** `COMMAND_NAMES[COMMAND_SDP_LOCK]` and `[COMMAND_SDP_UNLOCK]` still dereference (P-17.4)
- [ ] **Deletion:** `grep -rn "dev sdp" firestarter_app/` is empty; the `.ambr` diff matches its named expected shape (P-15, P-17.12)
- [ ] **mypy gate:** the hardened checker exits **2** on a planted aborted-mypy output, and a canary fixture's known error count is asserted as a floor (P-13)
- [ ] **mypy gate:** the watermark was lowered only in a commit that also fixed errors (P-13)
- [ ] **Gates:** `check_no_exists_proxy.py` green; `check_devtest_orchestrator.py` proven able to see a planted violation in a **new** helper (P-07, P-14)
- [ ] **Gates:** every pre-authored gate observed to actually FAIL on a planted violation before being called done (P-14, last row)
- [ ] **Claim gate:** targets resolve inside the checker's own phase dir; basenames carry this milestone's number; env seam and test module renamed; the checker's own suite run and its output recorded (P-11)
- [ ] **Claim gate:** the report renderer's own strings are covered by a claim scan, in the **app** repo where CI runs (P-12.1)
- [ ] **CI parity:** the suite run twice — once with `FIRESTARTER_FW_ROOT` at an empty dir, once with the sibling present — plus CI-scoped ruff, with no board attached for one run, before any `beta` push (P-18)
- [ ] **Channel:** `dev --help` pinned on BOTH channels via a subprocess that patches `__version__` before import, with positive AND negative membership assertions (P-19)
- [ ] **Removal-safety:** a comment at `eprom_operations.py`'s auto-unlock site AND a named test whose failure explains the coupled decision (P-21)
- [ ] **Labels:** `STATE.md:532` / `PROJECT.md:705` "v1.23+" corrected (P-17.11, P-22)
- [ ] **gh#20** triaged before or with the leg — an AT28C256 `dev test` already fails in the field (P-20.3)

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---|---|---|
| P-01 vacuous oracle (A == B) shipped | **HIGH** | every SDP result ever filed is void; a new beta, a retraction in the next release notes, and a corrected gh#12 follow-up. Caught in review: LOW |
| P-02 empty-read-back reads as equality | **MEDIUM-HIGH** | same class; any filed "HELD" result must be re-read to see whether the read-back was empty — recoverable **only if** the read-back hash and length are in `to_dict()`. Another reason for P-04.1 |
| P-09 inverted sensitivity shipped | **HIGH** | the leg reports OK exactly when the defect is present; there is no way to tell from the archive. Requires re-running on hardware nobody owns |
| P-20 a locked chip reaches a community member | **LOW technically, HIGH in trust** | a plain `firestarter write <chip> <file>` recovers it. Only low **if** the report told them so, in the word "rewrite" |
| P-13 mypy watermark lowered to a broken run's count | **MEDIUM** | revert the watermark, harden the gate, re-measure in a CI-equivalent env, fix, lower to the true count |
| P-15 `--snapshot-update` blessed unrelated drift | **LOW-MEDIUM** | `git diff` the `.ambr` against the previous tag and revert the unintended entries. Costly only if committed and shipped |
| P-16 four honesty tests deleted | **LOW** | recover from git history and retarget. Only low while anyone remembers they existed — which is why P-16.3's grep gate is worth three lines |
| P-11 claim gate passed against v1.23's artifacts | **MEDIUM** | the gate was never armed, so its `PASS:` in a SUMMARY is a false record and must be corrected; re-run armed and re-record |
| P-17 a `--pre` user's script breaks | **LOW** | release-notes mapping + gh#12 follow-up; blast radius is days of pre-release installs and no stable release ever carried the command |
| P-21 auto-unlock default changed later, dependency lost | **HIGH, deferred** | the deletion becomes retroactively wrong and the recovery path is gone. Prevention is the only real remedy |

---

## Pitfall-to-Phase Mapping

Proposed phase numbering (phases continue at **131**). **The ordering rationale is this project's own established gate-first pattern** (v1.12's baseline-and-gate-before-touching-firmware; v1.23 Phase 123's six fail-provable gates authored *before any firmware moved*): a milestone whose deliverable is an oracle must not build the oracle on a suite whose gates are known fail-open.

| Phase | Name (proposed) | Pitfalls owned | Verification |
|---|---|---|---|
| **131** | **Gate hardening & test-harness baselines** — the mypy gate, the fail-open sweep, the CI-parity recipe, the channel/snapshot harness, the claim-gate vocabulary | P-13, P-14, P-07 (derived subset test), P-10 (count gate), P-18 (recipe), P-11 (vocabulary + the two new target-resolution test legs) | primary `ci` job GREEN; hardened checker exits 2 on planted aborted output and on a missing canary; `check_no_exists_proxy.py` green; the recipe run and its two outputs recorded |
| **132** | **Retire `dev sdp`; re-home its honesty and gate-ordering tests** | P-15, P-16, P-17, P-21 (comment + named test), P-08 | `grep -rn "dev sdp"` empty; the four honesty assertion strings still grep-findable; `.ambr` diff matches its named shape; `COMMAND_NAMES` dereference test green |
| **133** | **The plan-derived SDP leg in `dev test`** — the oracle | **P-01, P-02, P-03, P-04, P-05, P-06, P-09, P-20, P-23**, P-12 (report strings) | the write-succeeded ⇒ BAD test; both-directions oracle test; four degenerate-read-back fixtures; routes R1–R6 tests; the `try/finally` + baseline-gate tests; the "erase"-forbidding grep; the op-registration parity test |
| **134** | **`write --sdp-relock`** | P-22, and the stale label fix | verify-FAIL ⇒ `sdp_lock.assert_not_called()` + `WARNING` + non-zero exit; gate-ordering cases inherited from 132 |
| **135** | **999.15 / gh#8 dev-tools channel gating** | P-19, P-17.9 | `dev --help` pinned on both channels with positive AND negative membership assertions; `channel.py` reused, zero new env-var gates |
| **136** | **Close: honesty ledger, armed claim gate, gh#12 follow-up** | **P-11 (armed), P-12**, P-21 (ledger + STATE row), P-25 | the claim gate armed and green with a `PASS:` naming **this** milestone's four artifacts; its own suite run and recorded; operator wording review completed as a non-`<automated>` step |
| — | cross-cutting | P-24 (name allowed requirement IDs at dispatch), P-18 (run the recipe every phase) | per-phase verification |

**Two ordering constraints worth stating explicitly:**

1. **131 before everything.** Any green suite reported by 132–136 is unverified until the mypy gate can fail and the fail-open sweep is done.
2. **The leg (133) before or with the deletion (132).** Deleting first opens a window in which the SDP capability has zero test coverage and the four honesty assertions exist nowhere. If the roadmap prefers deletion early to shrink 999.15's diff, put both in one phase and use `git mv`. (Sequencing note from the design record: whichever of the deletion and 999.15 lands first shrinks the other's diff, and v1.30 **deletes** a subcommand 999.15 would otherwise have to classify — so 132 before 135 either way.)

---

## Confidence per pitfall

| Pitfall | Confidence | Basis |
|---|---|---|
| P-01, P-02, P-03, P-04, P-05, P-06, P-07, P-08, P-16, P-17, P-19, P-20, P-23 | **HIGH** | direct first-party reads of the exact files and line numbers cited in this milestone's scope |
| P-13 | **HIGH** | reproduced locally this session; exact command output quoted |
| P-11 | **HIGH** | both checker copies read in full, including their own docstrings' recorded C-2/A3 findings; the failure mode is a direct consequence of `_HERE` + a still-existing sibling directory |
| P-15 | **HIGH** for the `.ambr:141` content and the project's `addopts`; **MEDIUM→HIGH** for syrupy's unused-snapshot default, cross-checked against syrupy 5.5.3's own `session.py`/`__init__.py` source, not docs alone |
| P-09, P-10, P-12, P-14, P-18, P-21, P-22 | **HIGH** on the mechanisms; **MEDIUM** on which specific downgrade an implementer will reach for (the routes are enumerated from the code; the likelihood ordering is judgement) |
| P-24, P-25 | **MEDIUM** | this project's own recorded incident history, not re-verified this session |

---

## Sources

**First-party source reads (HIGHEST confidence — the authoritative sources for this milestone):**

- `firestarter_app/firestarter/chip_test.py` — `generate_pattern:59`, `address_fold_byte:48`, `_diff_offsets:93`, `derive_plan:394`, `_DESTRUCTIVE_OPS:636`, `_MULTI_RUN_OPS:657`, `StepResult:662`, `_skip_result:685`, `run_plan:713`, `_id_step_closes_gate:800`, `_write_region_for:823`, `_run_step:865`, `_dispatch_step:903`, `_dispatch_read:975`, `_sample:1029`, `_dispatch_multi_run:1039`, `_RAN_VERDICTS:1209`, `count_applicable:1226`
- `firestarter_app/firestarter/cli_handlers.py` — `dev` group `:1171`, `_VERDICT_EXIT_CODES:1865`, `_ALWAYS_WRITES_NOTICE:2045`, `dev_test:2055`, `dev_sdp:2196-2230`
- `firestarter_app/firestarter/channel.py`, `sdp_capability.py:266`, `eprom_operations.py:1736 sdp_unlock` / `:1784 sdp_lock`
- `firestarter_app/tools/check_mypy_watermark.py`, `check_devtest_orchestrator.py`, `check_no_exists_proxy.py`, `check_sdp_capability_invariants.py`
- `firestarter_app/tests/` — `fw_presence.py`, `conftest.py`, `test_skip_census.py`, `test_characterization.py:242-330,470-530`, `test_dev_test_cmd.py:566-600,635-690`, `test_dev_sdp_cmd.py:125-558`, `__snapshots__/test_characterization.ambr:124-150`
- `firestarter_app/.github/workflows/ci.yml`, `pyproject.toml`
- `.planning/phases/122-close-…/check_permitted_claims.py` + `test_check_permitted_claims.py` + `fixtures/`
- `.planning/phases/123-non-regression-…/check_permitted_claims.py` + `fixtures/`

**Locally reproduced measurements (this session, 2026-08-03):**
- `mypy firestarter/ tests/` → `Found 1 error in 1 file (errors prevented further checking)` preceded by `pyproject.toml: [mypy]: python_version: Python 3.9 is not supported`
- `python3 tools/check_mypy_watermark.py` → `mypy errors: 1 (watermark: 35)` / `INFO: 34 below watermark` / exit **0**
- syrupy 5.5.3 installed; `pytest_sessionfinish` ORs `_syrupy.finish()` into `session.exitstatus`; `session.py:301` gates on `not self.update_snapshots and not self.warn_unused_snapshots`; project `addopts = "-ra -q"`

**This repo's own post-mortem record:**
- `.planning/PROJECT.md` §"Current Milestone: v1.30" (`:38-155`), §v1.22 / §v1.23 archives (`:32`, `:34`, `:231`)
- `.planning/STATE.md` — v1.30 context `:40-60`, Deferred Items `:60-100`, `:188-196`, `:379`, `:447`, `:534`, `:680-712`, `:1049`, `:1057`
- `.planning/RETROSPECTIVE.md:390`, `:404`, `:409`, `:431`, `:467`, `:724`
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` (all 157 lines; §5's three traps, §7's insertion points)
- `.planning/research/questions.md:195-220`
- Phase records: v1.12 GATE-03 (hollow gate), v1.21 Phase 121-02 RESEARCH C-5 / Pitfall 1a (unmapped op → `erase_eprom()` → OK), Phase 114.1 (absent-chip hard-fail), v1.22 Phases 116–122 (C-5 overclaim, inverted `(0x5555,0x20)` check, `/WE` HIGH), v1.23 Phases 123 (BASE-02/D-09 fail-open proxy) / 127 (mypy fail-open, `test_help_fw` channel split) / 130 (C-2, C-3, C-7, C-8)
- Open community issues: gh#20 (AT28C256 `dev test` FAIL, 2026-07-30), gh#18, gh#11, gh#12

**External (MEDIUM, cross-checked against installed source):**
- [syrupy README / releases — unused-snapshot handling and `--snapshot-warn-unused`](https://github.com/syrupy-project/syrupy/blob/main/README.md)
- [syrupy on PyPI](https://pypi.org/project/syrupy/)
- [syrupy issue #138 — filtering unused snapshots when specifying test nodes](https://github.com/tophat/syrupy/issues/138)

---
*Pitfalls research for: v1.30 SDP Surface Retirement & Behavioral Lock Proof — host-only, `firestarter_app`*
*Researched: 2026-08-03*
*Not committed — the research synthesizer commits all artifacts.*
