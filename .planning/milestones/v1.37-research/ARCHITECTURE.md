# Architecture Research — v1.36 `dev test` Fidelity

**Domain:** Host-side test-harness engine (`firestarter_app`), subsequent-milestone integration
**Researched:** 2026-09-02
**Confidence:** HIGH (every claim below was read from the working tree at
`firestarter_app@0a93999`, meta at `58bb8d80`; two claims were additionally
executed, not merely read — see §6.1 and §6.3)

**Method note.** This is not an ecosystem survey. Every file/line citation was opened
on disk. Where the milestone brief's line numbers had drifted from HEAD, the real
number is used and the drift is called out. Three line ranges in the brief are stale:

| Brief says | Actually at HEAD | Note |
|---|---|---|
| `serial_comm.py:520-526` and `:536-541` (re-sync) | `serial_comm.py:485-490` and `:500-505` | Same two sites, ~35 lines earlier |
| `diagnostic_report.py:316-355` (`dedup_fingerprint`) | `diagnostic_report.py:186-241` | Body at `:211-241`, the hashed triple at `:213-214` |
| `_merge_cycle_results` | `_aggregate_cycle_results`, `chip_test.py:1280` | Function does not exist under the brief's name |

Confirmed exactly as stated: the gate at `chip_test.py:3100`; `classify_fingerprint` at
`:162`; `mask_write_pattern` at `:2057`; `uv_slot_starts` at `:2171`;
`REGION_POLICY_UV_SLOT` at `:382`; `SCHEMA_VERSION = "1.7"` at
`diagnostic_report.py:48`; `NOT_MEASURED` at `:49`; `vpp_mv`/`vpe_mv` at `:571-572`
and `:638-639`; `banner.locked_steps` at `:733` and `:737`; `build_flags`'s
`FLAG_SKIP_BLANK_CHECK` map at `eprom_operations.py:279`; `self.comm = None` at
`eprom_operations.py:547`; the sentinel at `tests/test_chip_test_sdp_leg.py:827`.

---

## 1. The architecture as it stands

### 1.1 Layer map

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ORCHESTRATION      cli_handlers.dev_test (:2345-2499)                    │
│  - derive_plan -> run_plan -> report assembly -> render/persist/submit    │
│  - owns every assignment onto DiagnosticReport (the "derive-in-engine /   │
│    assign-in-handler" seam, stated at :2414-2418)                         │
├──────────────────────────────────────────────────────────────────────────┤
│ DECLARATION        chip_test.derive_plan (:486-855)                      │
│  - PURE. db.get_eprom + db.convert_to_programmer only. No operator, no    │
│    chip access, no resolve_chip. Decides op set, write_region,            │
│    region_policy, cycle_payload, is_uv -- ONCE, read-only downstream.     │
├──────────────────────────────────────────────────────────────────────────┤
│ EXECUTION          run_plan (:1582) -> _run_cycle_block (:1475)          │
│                    -> _run_step (:2349) -> _dispatch_step (:2493)        │
│  - WriteContext (:1132) is the ONLY execution-time state carrier          │
│  - gates: destructive_gate_closed (:1646), baseline_gate_closed (:1656)   │
├──────────────────────────────────────────────────────────────────────────┤
│ DISPATCH ARMS      _dispatch_id (:2603)  _dispatch_read (:2626)          │
│                    _dispatch_multi_run (:2922)  _dispatch_sdp (:3158)    │
│                    _dispatch_sdp_leg (:3211)                             │
├──────────────────────────────────────────────────────────────────────────┤
│ OPERATOR           eprom_operations.EpromOperator                        │
│  - _operation_context (:504-542) -> _setup_operation -> find_and_connect  │
│  - _disconnect_programmer (:544-547) tears self.comm down after EVERY call│
├──────────────────────────────────────────────────────────────────────────┤
│ TRANSPORT          serial_comm.SerialCommunicator                        │
│  - find_and_connect (:943) IS the command send (CAP-02, :824-829)         │
│  - _read_and_parse_lines: two re-sync sites at :485-490 and :500-505      │
├──────────────────────────────────────────────────────────────────────────┤
│ SIDE CHANNEL       hardware.HardwareManager  (its OWN connect path)      │
│  - _sample_one_voltage (:376-437), sample_vpp_mv (:440), sample_vpe_mv    │
│    (:445), read_programmer_identity (:151)                                │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                     REPORT (a pure consumer, imports chip_test)
        diagnostic_report.DiagnosticReport.to_dict (:771-790)
```

### 1.2 The two invariants everything else hangs off

**I-1 — `derive_plan` is pure and guard-bypassing by design.** Its docstring
(`chip_test.py:487-521`) and the section comment above it (`:263-273`) both state it: it
reads frozen DB fields, never `resolve_chip`, never the operator, never the chip. This is
why it can be swept over all 746 DB rows in a unit test with no hardware. **Any design
that needs `derive_plan` to consult run-time evidence destroys this property and with it
the entire structural-test strategy the milestone depends on.**

**I-2 — `plan.steps` and `results` are positionally aligned.** Three consumers assume it:

- `_run_cycle_block` returns exactly `len(steps)` results, in step order
  (`chip_test.py:1578-1580`, and its docstring says so at `:1484-1487`).
- `count_applicable` computes `M = sum(supported steps) + len(locked_destructive)`
  (`chip_test.py:3532-3535`) and `N = len(ran results)` (`:3536`).
- `DiagnosticReport._steps_list` (`diagnostic_report.py:750-769`) locates the write step by
  index into `plan.steps` (`_write_step_index`, `:642-666`) and then passes that `Step`
  into the result row at the **same index** in `results`.

---

## 2. Q1 — Where does the evidence-gated sequencing decision belong?

**Recommendation: neither of the two given options in isolation, and explicitly NOT a
new layer between them. Split the decision along the pure/impure line that already
exists — `derive_plan` DECLARES, the dispatch layer EVALUATES, and the run-time
evidence travels on the existing `WriteContext`.**

### 2.1 Why not plan-time (static, inside `derive_plan`)

`derive_plan` already owns the *static* half of "this op tells you nothing," and does it
well — three existing NA arms are exactly this rule:

- blank-check NA on SRAM/FRAM: "volatile/byte-rewritable, no factory-blank state"
  (`chip_test.py:656-664`)
- blank-check NA on auto-erase-on-write protocols: "no step in this plan can ever leave
  the device blank" (`:665-677`)
- erase NA arms (`:743-780`) — four distinct reasons, none naming a flag.

But the v1.36 rule is *not* static. `not all(outcomes)` is unknowable at plan time by
construction: `derive_plan` never touches the chip (I-1). Pushing it there would require
handing `derive_plan` an operator, which breaks the whole-DB sweep and the
guard-bypassing contract in one move.

### 2.2 Why not run-time-only (a bare `if not all(outcomes)` at `:3100`)

The todo (`.planning/todos/pending/2026-08-30-gate-fingerprint-readback-on-step-failure.md`)
proposes exactly `if collect_fingerprint and op in (...) and not all(outcomes):`. **That
is measurably insufficient at HEAD, because the repeat CYCLE landed after that todo was
written.** Under `_run_cycle_block`, `_run_step` is called with `runs=1`
(`chip_test.py:1546`) and `collect_fingerprint=final` where `final = cycle == cycles - 1`
(`:1538`, `:1549`). So inside `_dispatch_multi_run`, `outcomes` is a **one-element list
describing the final cycle only**.

Consequence: a run whose cycle 1 failed and cycle 2 passed folds to `marginal`
(`_aggregate_cycle_results`, `chip_test.py:1315-1317`) but the local `outcomes` on the
final cycle is `[True]`, so the gate closes and **the fingerprint is dropped from exactly
the AM27C020-shaped run the metric exists for** (write#1 60/64 byte-exact, write#2 0/64 —
recorded in `.planning/PROJECT.md` §v1.18 and in the cost-model note).

That is the decisive argument: the gate must read **run-level** evidence, not
this-invocation `outcomes`.

### 2.3 Why not a new layer between plan and execution

A layer that rewrites `Plan` between `derive_plan` and `run_plan` — dropping or replacing
steps once evidence arrives — breaks I-2 three ways at once:

- `count_applicable`'s `M` (`chip_test.py:3532-3535`) is computed off `plan.steps`. Drop a
  step and the banner silently reads "N of M" against a plan that is not the one derived.
- `_write_step_index` (`diagnostic_report.py:642-666`) returns an index into `plan.steps`
  which `_steps_list` (`:750-769`) then compares against `enumerate(self.results)`. A
  length or ordering skew silently attaches `write_coverage` to the **wrong row**.
- `_run_cycle_block`'s own contract ("Returns exactly `len(steps)` results, in the SAME
  order") would need rewriting.

And the structural-sentinel argument cuts the other way from how it is usually stated:
the test can only inspect what `derive_plan` returns. If a middle layer is what actually
decides what runs, then **the object the test inspects is no longer the object that
executes**, and the sentinel becomes decorative. Keep exactly one plan object.

### 2.4 The recommended shape

```
derive_plan (pure)                        run_plan / dispatch (impure)
─────────────────────                     ─────────────────────────────
Step.<declared oracle>          ────────► read by _dispatch_multi_run /
  (set once, read-only)                     _dispatch_read

                                          WriteContext (chip_test.py:1132)
                                            + run-level evidence ledger
                                            (the new field)
                                              ▲
                              _run_cycle_block │ writes it per cycle
                              (chip_test.py:1550-1570, beside the two
                               assignments it already makes there)
```

`WriteContext` is the correct home and is *named* for this job. Its own docstring says it
"carries the MASK decision, which can only be made at execution time because it reads the
chip" (`chip_test.py:1135-1137`), and it already threads three run-time facts through the
step loop: `chip_is_blank` (set at `:1557-1561` and `:1765-1772`), `target`/`refusal` (set
at `:1562-1566` and `:1774-1780`), and `cycle_targets`/`cycle_index` (`:1160-1169`).

Add a fourth: a small ledger of per-op run-level outcomes, written in the same place the
other two are written (inside the cycle loop, `chip_test.py:1550-1570` — the comment there
already explains why the assignments must happen *inside* the cycle), and read by
`_dispatch_multi_run` beside `_cycle_target(write_context)` (`:2989-2991`).

**Trade-offs, stated honestly:**

| Option | Structural test can see it | Report can export it | Handles cycle-1-fail/cycle-2-pass | Preserves I-1 / I-2 |
|---|---|---|---|---|
| Plan-time only | yes | yes | n/a — cannot express the rule | breaks I-1 |
| Run-time only (`outcomes` at `:3100`) | **no** | no | **no** (§2.2) | yes |
| New middle layer | inspects the wrong object | yes | yes | **breaks I-2** |
| **Declare in plan / evaluate in `WriteContext`** | yes (the declaration) | yes (the declaration) | yes | yes |

The cost of the recommendation: the declaration and the evaluation can drift — a `Step`
could declare an oracle the dispatcher does not honour. Mitigate exactly the way this
module already mitigates the same risk for `_MULTI_RUN_OPS` (`chip_test.py:939`,
fail-closed guard at `:2986-2996`): a closed module-level vocabulary plus a fail-closed
arm, so an unrecognised declaration refuses rather than defaults.

---

## 3. Q2 — How to express "this operation would carry no information"

**Recommendation: a pure relational predicate over `Plan.steps`, exported from
`chip_test.py`, swept over the whole database by one test. NOT a per-step declared
precondition, and NOT a post-hoc assertion over results.**

### 3.1 Why a per-step declared precondition fails as the enforcement mechanism

The invariant the milestone actually needs is **relational**, and stated as such in
`.planning/PROJECT.md:73-77`: *"dropping the unconditional read-back is safe only because
a verify follows every write in the same cycle."* That is a property of a **pair** of
steps, not of one step. A field on `Step` cannot express it.

Worse, a declared precondition is **self-certifying**: a future author who adds a write
step with no verify behind it simply declares no precondition, and the test passes green.
The predicate must be *derived from the emitted step list*, never from an annotation the
same author wrote.

(There is still a role for a declared field — see §3.4 — but it is a **disclosure** role,
not an enforcement role.)

### 3.2 Why a post-hoc assertion over results fails

A results-level assertion only fires when someone actually runs that plan, on that chip,
on hardware. The failure mode being prevented is *a future plan shape*, which may never be
run before it ships. It must be provable from `derive_plan` alone, offline, over the whole
DB.

### 3.3 The recommended shape (capability/oracle predicate)

A pure function beside `cycle_block_bounds` (`chip_test.py:1236`), which is already the
module's precedent for *relational reasoning over `plan.steps`* — it finds a maximal run
of consecutive ops and enforces that the block opens on a write (`_CYCLE_BLOCK_START_OPS`,
`:1228-1234`). The new predicate is the same species:

```python
def write_steps_carrying_no_oracle(plan: Plan) -> list[str]:
    """Every executable write-shaped step with no verify behind it in the
    same cycle block. EMPTY list == the plan is safe to run without the
    unconditional fingerprint read-back. Pure; no operator, no chip."""
```

Return **violations**, not a bool: the failure message must name the chip and the op, the
way `test_shipped_ops_never_reach_sdp_arm`'s messages do
(`tests/test_chip_test_sdp_leg.py:866-872`).

The test that consumes it sweeps the real database. The precedent for that sweep already
exists and should be reused rather than reinvented: `tests/test_erase_flag_invariants.py`
`_all_rows` (`:126-132`) walks `db.proms` as `{manufacturer: [chip_record, ...]}`, and its
sibling asserts the **746** total (`:154-161`) so the sweep cannot silently go vacuous.
That file's module docstring carries an explicit **anti-vacuity rule** and a worked
example of how a top-level scan over `db.proms` iterates manufacturer keys instead of chip
records and makes every downstream assertion pass for free (`:108-118`). Copy that
discipline verbatim; it is the single highest-risk failure mode for this test.

The sweep must run over **every reachable `write_scope`**, i.e. `"full"` and `"partial"` —
`_resolve_write_scope` (`cli_handlers.py:2438-2470`) returns only those two, and
`"none"` is library/test surface only (`chip_test.py:844-846` says so explicitly).

**Anti-vacuity legs the test must carry (all three, or it proves nothing):**

1. The sweep visited ≥ 746 chip records (pin the number, as `:154-161` does).
2. It found a non-zero number of **executable write steps** — otherwise the predicate was
   asked about an empty set.
3. A planted counter-example (a hand-built `Plan` with a write and no verify) makes the
   predicate return a non-empty list. This is the mutation proof that
   `test_shipped_ops_never_reach_sdp_arm` earned by monkeypatching `_SDP_OPS`
   (`tests/test_chip_test_sdp_leg.py:884-887`) and that the recorded mutation was *seen*
   to fire (`:840-843`). Without leg 3 the test is a hollow detector — the exact tech-debt
   this project has already booked once (`tools/check_devtest_orchestrator.py:47-52`).

### 3.4 The declared field's real job: disclosure, not enforcement

After the gate lands, a passing write step exports `"fingerprint": null`
(`diagnostic_report.py:719-721`). To every triager and to both skill consumers that is
indistinguishable from "the fingerprint failed to compute." The plan-declared field is
what lets the report say *why* — and it is also what §6.1's blast-radius problem needs.
Model it on the three closed string-constant vocabularies this module already carries
(`OP_*` at `:314-321`; `REGION_POLICY_*` at `:380-382`; `CYCLE_PAYLOAD_*` at `:400-402`),
each of which is "set exactly once by `derive_plan`, read-only downstream."

---

## 4. Q3 — The seam for counting `serial_comm.py` re-sync events

**Recommendation: instance counters on `SerialCommunicator`, drained onto `EpromOperator`
at the single teardown point, read by `cli_handlers.dev_test` into `TransportHealth`.
Zero new imports in either direction. This exact pattern already ships in this codebase
for the identical problem.**

### 4.1 The constraint that rules out the obvious answers

The two events are per-connection (`serial_comm.py:485-490`, `:500-505`), and the
connection is destroyed after every operator call by `_disconnect_programmer`
(`eprom_operations.py:544-547`). **A counter that lives only on the comm is unreadable by
the time the caller gets control** — this is not speculation, it is the measured finding
already recorded in `chip_test.py:3232-3241` about the `0x86` ack, and again in
`cli_handlers.py:2369-2378` about `programmer_info`.

A module-level global in `serial_comm.py` would survive teardown, but it bleeds across
pytest cases and across the `HardwareManager` side channel (which opens its own comms,
`hardware.py:407`) — attributing a sampler's re-sync to the chip's write step.

### 4.2 The precedent to copy, by name

`EpromOperator.last_firmware_error_code` / `last_firmware_error_message`
(`eprom_operations.py:402-403`). Their `__init__` comment states the exact reasoning this
problem needs: *"the operation context's finally tears down `self.comm` but never the
operator, so these survive the call that set them"* (`:396-397`). They are set in the
`EpromOperationError` arm of `_run_state_machine` (`:594-600`), cleared on entry
(`:571-573`), and read back through a `getattr`-with-defaults helper —
`chip_test._firmware_error` (`:2895-2921`) — precisely so every hand-rolled test double in
the suite degrades to "nothing recorded" instead of raising.

Apply it unchanged:

| Where | What | Why there |
|---|---|---|
| `serial_comm.py` `__init__` (beside `seen_message_ids`, `:185`) | two integer counters, per-connection instance state | the comment at `:180-185` already establishes "per-connection instance state, not shared across connections" as this class's policy |
| `serial_comm.py:485-490`, `:500-505` | `+= 1` beside the existing `logger.warning` | the ring-fenced generator body is touched by two increments only; no control-flow change |
| `eprom_operations.py:544-547` | drain into operator-level totals **before** `self.comm = None` | **this is the only assignment of `self.comm = None` in the module** (verified: `grep` finds `self.comm =` at `:491`, `:547`, `:1355`, `:1741` — `:547` is the sole `None`), so drain-at-teardown is complete by construction and that completeness is itself testable |
| `cli_handlers.dev_test` | assign onto `TransportHealth` after `run_plan` returns | the module's stated seam: derive in the engine, assign in the handler (`:2414-2418`), same as `_make_sampler` does for the rails (`:2211-2219`) |

Import direction is unchanged: `serial_comm` imports nothing new; `eprom_operations`
already imports `serial_comm`; `diagnostic_report` keeps importing only `chip_test`
(`diagnostic_report.py:32-42`) and stays the "orchestrator only" module its docstring
promises (`:15-19`).

### 4.3 Two consequences to plan for

- `_is_transport_suspect` (`diagnostic_report.py:120-132`) fires at
  `_SUSPECT_THRESHOLD = 5` (`:57`) on any counter that is **present and ≥ 5**. The moment
  real counters land, `transport_suspect` becomes reachable for the first time. The
  threshold was chosen while dormant and has never been exercised against a real
  distribution — it needs a stated basis or it is a fabricated verdict. `NOT_MEASURED`
  (`:49`) must remain for genuinely unwired counters (`retries`, `timeouts` if not wired),
  per RPT-C2.
- The `HardwareManager` side channel's comms (`hardware.py:407`, `:186`) never pass
  through `EpromOperator`, so their re-syncs are **not** counted by this seam. That is a
  defensible scope line — the sampler is a diagnostic, the chip ops are the subject — but
  it must be *stated in the report's own semantics*, not left implicit, or the counter
  reads as whole-run when it is operator-path-only.

---

## 5. Q4 — Where session reuse belongs, and what breaks

### 5.1 The finding that reframes R4

**`find_and_connect` IS the command send.** `_probe_port` sends the caller's actual
command dict as the handshake (`serial_comm.py:824-829`: *"CAP-02: send the user's actual
command straight away. The dedicated `CMD_FW_VERSION` pre-probe this replaces cost a full
command exchange (2 acks) on every single connect"*). So today **one connection ≡ one
command, by construction.** "Session reuse" therefore does not mean "keep a socket open";
it means **issue a second `send_json_command` on an already-open, already-validated
link** — a genuine protocol-sequencing change, not a resource-pooling tweak.

Two corollaries the seed and the cost note do not state:

- **The seed's cheap sub-step is not available host-only.** Folding `sample_vpp_mv` and
  `sample_vpe_mv` into one monitor read (seed §R4, "−2 connects per write step") requires
  a firmware command that returns both rails: `_sample_one_voltage` is parameterised on
  `state` and is called once per rail with `COMMAND_READ_VPP` / `COMMAND_READ_VPE`
  (`hardware.py:400-437`, `:440-448`). v1.36 is host-only by activation decision
  (`.planning/PROJECT.md:102-104`), so **this sub-step is out of scope and its −2 connects
  must not be counted in any v1.36 saving.**
- The sampler's connects live in `hardware.py`, not `eprom_operations.py`. Session reuse
  in the operator does **not** reduce them. Of the 32 connects for an at28c256 run, the
  4-per-write-step sampler cluster (cost note §4) is untouched by R4 as scoped.

### 5.2 Where it belongs

`EpromOperator._operation_context` (`eprom_operations.py:504-542`) is the natural
boundary: it is the one place setup and teardown are paired, and its `finally` is the sole
caller of `_disconnect_programmer` on the operation path (`:540-542`). The lease should be
owned one level up — a context manager on `EpromOperator` that `run_plan` opens once and
that `_setup_operation` consults instead of always calling `find_and_connect` (`:491`).

`run_plan` is the right lease holder: it already has a bare `try/finally` around the whole
step loop for the cleanup registry (`chip_test.py:1707-1712`, `:1836-1866`), with a
carefully-reasoned comment about why it is a *bare* finally (it must reach
KeyboardInterrupt/SystemExit while letting them propagate). A lease released in that same
`finally` inherits all of that reasoning for free — but note `chip_test.py` **must not
learn about transport**: the module docstring promises it "sets no VPP and calls no
firmware method itself" (`:15-19`) and `tools/check_devtest_orchestrator.py` enforces the
orchestrator-only contract by AST. So the lease must be an **opaque operator-side context
manager**, invoked like the existing opaque `sampler` callable is (`run_plan`'s docstring,
`chip_test.py:1615-1621`), never a comm object chip_test can see.

### 5.3 What breaks — the honest list

| Site | What it says today | Effect |
|---|---|---|
| `eprom_operations.py:552` | `_run_state_machine`: `if not self.comm: return False, "Not connected"` | Still correct; a lease that fails to open leaves `comm` `None` and this path is the graceful degradation. Keep. |
| `eprom_operations.py:1888-1897` | the `0x86` SDP-skip ack MUST be read inside the `with` block "that block's `finally` calls `_disconnect_programmer()`" | Still correct and still the safe place. Do **not** relax it to a post-block read just because the comm now survives — that couples the check to the lease's lifetime. |
| `chip_test.py:3232-3241` | ⚠ the `0x86` ack "is UNOBSERVABLE from this module... Research's truth-table branch 5 is THEREFORE NOT IMPLEMENTABLE AS WRITTEN" | **Becomes false.** This is a recorded, load-bearing non-claim behind the SDP leg's `(False, ·) -> marginal` design. It must be re-stated, not quietly deleted — and re-opening branch 5 is *not* in v1.36 scope. |
| `cli_handlers.py:2369-2378` | "there is no live comm to read `programmer_info` off of after `run_plan` returns without opening a new, extraneous connection" | **Becomes false.** The identity read (`:2380`) could then be folded, saving one more connect. Tempting; it also couples the report's identity fields to the lease. Recommend: leave the identity read alone in v1.36 and record the now-stale comment. |
| `chip_test.py:1601-1605` (`run_plan` docstring) | "One step's BAD verdict or raised exception NEVER aborts the rest — each body has its own try/except" | **The real risk.** Today every step reconnects from scratch, which is a hard resync. A shared link means a desynced transport poisons every later step and turns one chip finding into a wall of BAD. **Mandatory mitigation: any `SerialError`/`SerialTimeoutError` invalidates the lease, and the next step reconnects.** Without that, session reuse converts the harness's central non-fatal-step guarantee into a false one. |
| `tests/test_eprom_operations.py:87-91` | explicitly sets `operator.comm = None` as the "not connected" state | Contract preserved by the `:552` guard above; expect no change. |
| ~20 test doubles across `tests/` assign `operator.comm = make_comm()` | they inject a live comm directly | A lease that only *adds* a reuse path (falling back to `find_and_connect` when no lease is held) leaves every one of these green. A lease that *replaces* the connect path breaks all of them. Prefer additive. |

### 5.4 Do not scope R4 before measuring

`.planning/PROJECT.md:113` makes this a milestone constraint, and the cost model states
its own limit: *"Per-connect cost in seconds (port busy; counts only)"*
(`dev-test-sequence-cost-model.md`, "What this note does not establish"). The counts are
structural and validated (13 predicted / 13 observed); the seconds are not measured at
all. On Uno-class boards a port open triggers the DTR auto-reset and bootloader wait,
which is likely the dominant term and is board-class-dependent — so the measurement must
be **per board class**, not one number.

---

## 6. Traps found while reading (anti-patterns, and one that blocks a stated goal)

### 6.1 ⚠ BLOCKING — R2 as specified re-keys `dedup_fingerprint` on every passing run

`.planning/PROJECT.md:95-99` states the blast-radius gate: `dedup_fingerprint` must stay
byte-identical, and *"Not one field being added, filled or deleted is in that hash today."*
That is true of the **report** fields. It is **not** true of the fingerprint read-back.

`dedup_fingerprint` hashes, per step:

```python
cls = result.fingerprint.classification if result.fingerprint else ""   # :213
parts.append(f"{result.op}={result.verdict}:{cls}")                     # :214
```

A **passing** write or verify step carries a `Fingerprint` today, and its classification
is `indeterminate` — bucket 4, because `bad == 0` skips the address-line loop
(`chip_test.py:216`), `ff_ratio` on an address-derived pattern is far below the 0.98
threshold (`:146`, `:200`), and `repeat_divergent` is `False` not `True` (`:244`).
Executed, not inferred:

```
$ python3 -c "... classify_fingerprint(p, p, repeat_divergent=False, addr_base=0) ..."
passing full-device write/verify -> indeterminate bad= 0 ff_ratio=0.00391
passing UV slot                  -> indeterminate bad= 0 ff_ratio=0.00391
```

So today a clean run hashes `write=OK:indeterminate`; drop the read-back and it hashes
`write=OK:` — **every passing chip's dedup group re-keys, every `count_agreeing` group
resets, and Phase 114's GRAD-01 promotion ladder is disturbed.** That is precisely the
outcome the milestone's own blast-radius gate forbids.

**Recommended resolution — synthesize, do not measure.** On a passing step, attach a
`Fingerprint` built from what the run **already knows** rather than from a read-back:
`total = region_length`, `bad = 0`, `bad_pct = 0.0`, `classification = FP_INDETERMINATE`,
and an `evidence` dict that records `ff_ratio: None` plus an explicit "no read-back was
performed" key. This is defensible on the project's own honesty terms: the firmware
compared every byte during `memory_verify_execute` and found zero mismatches
(`firestarter/src/proms/memory.cpp:377-396`), so `bad = 0 / total = N` is a
firmware-established fact; the only thing not measured is `ff_ratio`, and it is honestly
`None` rather than fabricated. It is arguably *more* honest than today's value, which
computes `ff_ratio` over bytes the firmware had already validated.

This needs its own named plan decision and its own test: **"a passing write/verify step's
`dedup_fingerprint` contribution is byte-identical before and after the read-back gate."**
Provable purely in unit tests; no hardware.

Rejected alternatives, recorded so they are not re-litigated: accepting the re-key
(forbidden by the milestone); excluding `classification` from the hash when the verdict is
OK (re-keys new reports against old bodies, same damage, plus it blinds dedup to a
classification change on a passing run).

### 6.2 ⚠ The cycle loop already drops the fingerprint on a firmware-refused write

`_run_cycle_block` sets `hardware_refused = True` on any non-`None` `error_code` and
`break`s out of the cycle loop (`chip_test.py:1567-1570`). With `cycles = 2`, cycle 0 has
`final = False` (`:1538`) so `collect_fingerprint = False` (`:1549`), and cycle 1 never
runs. **A firmware-refused write therefore produces no `Fingerprint` at all today** — a
pre-existing fidelity hole, on exactly the class of failure (the VPP-out-of-range refusal
`0xA9` named in the retry-guard comment at `:1515-1530`) where a fingerprint would be most
useful. Not caused by v1.36, but v1.36 is the milestone that must not make it worse, and
the run-level ledger from §2.4 is what makes it fixable.

### 6.3 The detected chip-ID is recovered by scraping a prose string

RPT-A1 (`chip_id_actual` on a passing id check) has a cleaner fix than the requirement
implies. `_dispatch_id` **has** the detected id (`chip_test.py:2604`) and throws it away —
it survives only inside the human-readable `reason` text at `:2617-2620`. `_chip_id_fields`
then recovers it with `r.reason.rsplit("0x", 1)[-1]` and `int(..., 16)`
(`cli_handlers.py:2172-2179`), guarded by `"mismatch" in r.reason.lower()`.

**Recommendation: carry the detected id as a structured field on `StepResult`** (additive,
`None` on every other op — the same discipline `write_target` follows at
`chip_test.py:1058-1060`) and have `_chip_id_fields` read the field. Do not extend the
string-scraping to also parse the *passing* case; that would make the report's identity
fields depend on prose wording that `tools/check_diagnostic_report_claims.py` may later
require changing.

### 6.4 `banner.locked_steps` deletion is narrower than it looks

`BannerCounts.locked_steps` (`chip_test.py:3512`) is still asserted by live tests for
`write_scope="none"` plans (`tests/test_chip_test.py:2324`, `:2346`). What is dead is the
**export** at `diagnostic_report.py:733` and `:737`, because `_resolve_write_scope`
(`cli_handlers.py:2438-2470`) returns only `"full"` or `"partial"`. RPT-B2 as drafted also
deletes `Plan.locked_destructive`, which would take `count_applicable`'s `M` term
(`chip_test.py:3532-3534`) and those tests with it. **Delete the export; adjudicate the
dataclass field separately.** The split-out todo
(`.planning/todos/pending/delete-banner-locked-steps-dead-field.md`) owns this — land it
once.

### 6.5 Forward-only deletion has a real fixture corpus, in the meta repo

The frozen schema-1.2 fixtures are `.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md`
and `dev-test-at28c256-populated-identity.md` — two files, in the **meta** repo, carrying
`vpp_mv: 11800` and `"locked_steps": []`, with headers that forbid regeneration. There is
**no** report fixture corpus inside `firestarter_app/tests/fixtures/` (verified: 22 files,
all `planted_*` gate counter-examples plus `fake_firestarter`). So RPT-E2/E3's
"asserted against the frozen fixtures" requires either vendoring those two bodies into
`firestarter_app/tests/` or building a new corpus captured at HEAD. **This is a build-order
dependency: the corpus must exist and be green before any field is added, filled or
deleted.**

Both parsers accept `schema_version` by presence only
(`firestarter_app/tools/parse_devtest_issue.py:99`, and a live fixture carries
`"9.9-future"` per `tests/test_parse_devtest_issue.py:138`), so the 1.7 → 1.8 bump needs
no parser change. Neither skill consumer reads `steps[].fingerprint`; both read
`dedup_fingerprint` only (`.claude/skills/devtest-triage/scripts/devtest_issues.py:161-166`,
`.claude/skills/devtest-rootcause/scripts/seed_debug_session.py:294`) — which is exactly
why §6.1 matters and why the per-step schema growth does not.

### 6.6 R3's sampled read must not silently change `divergence`'s meaning

`_dispatch_read` (`chip_test.py:2626-2672`) emits `divergence` only when the two whole-run
sha256s differ, and the dict then carries exact whole-device `cmp_len`/`bad`/`pct`/
`first_offset` (`:2655-2668`). Replace the second sweep with a bit-structured sample and
`cmp_len` silently becomes a **sampled subset size** under the same key. Since RPT-A3
exports `divergence` for the first time in the same milestone, the two changes collide:
the field arrives in the schema already ambiguous. Either the sample escalates to a full
second read before emitting `divergence` (the seed's own escalation rule), or the emitted
dict names its own basis.

### 6.7 The UV `FLAG_SKIP_BLANK_CHECK` change has a ready-made call shape — and a gate to respect

`_dispatch_multi_run` calls `write_eprom` with no `operation_flags`
(`chip_test.py:3070-3075`), so `operation_flags` defaults to `0` and
`FLAG_SKIP_BLANK_CHECK` (`0x08`, `constants.py:122`) is clear. The SDP leg already passes
flags **positionally** through the same operator method
(`chip_test.py:3319-3325`), so the call shape exists and needs no new operator signature.

Two constraints on how the bit is chosen:

- It must be keyed on `Step.region_policy == REGION_POLICY_UV_SLOT` (`chip_test.py:382`),
  the plan-time decision — never re-derived from `electrical-type` at dispatch time. `Plan.is_uv`
  is "decided EXACTLY ONCE ... Downstream may only READ it" (`:451-457`), and the
  `algorithm == 0x0B` proxy matches only 32 of 301 UV parts (`:461-463`).
- `tools/check_devtest_orchestrator.py` bans a **dict literal** in `chip_test.py` whose
  keys intersect the wire vocabulary, `flags` included (`:19-26`). A positional int
  argument is not a dict literal, so the SDP leg's existing shape is the compliant one.
  Do not build a flags dict.

The safety argument is already written and holds: `mask_write_pattern` is `P = C & D`
(`chip_test.py:2057`), monotone 1→0 only, with a verify immediately behind it in the same
cycle.

### 6.8 Adding a helper to `cli_handlers.py` can silently escape the orchestrator gate

`tools/check_devtest_orchestrator.py` scans `cli_handlers.py` narrowed to a **fixed name
list**, `_HANDLER_FUNCTION_NAMES` (`:152-164`): `dev_test`, `_verdict_code`,
`_overall_exit_code`, `_dev_test_exit_code`, `_sanitize_chip_token`, `_is_uv_eprom`,
`_resolve_write_scope`, `_chip_id_fields`, `_is_interactive`, `_make_sampler`. **A new
co-located helper that is not added to that set is not scanned** — the gate fails open for
it. Any new `dev_test` helper (transport-counter assembly, elapsed timing) must be added
to that frozenset in the same commit.

---

## 7. Cost characteristics per chip class (what the design must not flatten)

| Class | Example | What must survive | Where enforced |
|---|---|---|---|
| UV-EPROM | m27c512, am27c020 | full-device blank-check kept (cheapest primitive per byte, and blankness is operator-actionable); top-down slot probe; tranche staging across cycles | blank-check step `chip_test.py:678`, placement `:680-683`; `uv_slot_starts:2171`; `_uv_cycle_targets:1419` |
| SRAM/FRAM | fm1608 | `CYCLE_PAYLOAD_ALTERNATE` — a volatile part has no blank state and needs the forced 0→1 | `chip_test.py:564-566`, `_alternating_cycle_targets:1394` |
| flash4 / 0x05 | w29c040 | boot-block carve-out; erase NA; blank-check NA | `full_device_region:2185`; `chip_test.py:583-604` |
| SDP leg / 0x0D | at28c256 | **untouched by the read-back gate.** `_read_region` there IS the verdict; the length gate (`:3346-3361`) and degeneracy gate (`:3363-3382`) both need real bytes | `_dispatch_sdp_leg:3211`, and its own docstring `:3325-3335` |
| `--fast` | any | stays the weaker single-run mode and keeps re-keying via `repeat_policy_tag` | `chip_test.py:1081-1104`; `dedup_fingerprint:216-221` |

R4 is the **only** rule that helps the at28c256 SDP leg (12 of its 32 connects for ~3 KB),
and it is also the rule whose payoff is unmeasured. That tension is the milestone's main
sequencing problem — see §9.

---

## 8. New vs modified — the integration inventory

### New

| Component | Home | Purpose |
|---|---|---|
| Relational plan predicate (§3.3) | `chip_test.py`, beside `cycle_block_bounds:1236` | pure; returns violations |
| Whole-DB structural sentinel test | new `tests/test_devtest_no_information_ops.py` | sweeps 746 rows × 2 scopes; 3 anti-vacuity legs |
| Run-level evidence ledger field on `WriteContext` | `chip_test.py:1132-1169` | run-level outcomes, written in the cycle loop |
| Declared-oracle field + closed vocabulary on `Step` | `chip_test.py:406-439` + constants beside `:380-398` | disclosure; exported by the report |
| Two re-sync counters | `serial_comm.py` `__init__` beside `:185` | per-connection instance state |
| Operator-level counter totals + drain | `eprom_operations.py:544-547` | survives comm teardown |
| `detected_id` on `StepResult` (§6.3) | `chip_test.py:1025-1061` | replaces prose scraping |
| Report fixture corpus (§6.5) | `firestarter_app/tests/fixtures/` | RPT-E2/E3's oracle |
| Operator session lease (R4, conditional) | `eprom_operations.py` around `_operation_context:504` | opaque to `chip_test` |

### Modified

| Site | Change |
|---|---|
| `chip_test.py:3100` | gate reads the run-level ledger, not local `outcomes` (§2.2) |
| `chip_test.py:3070-3075` | pass `FLAG_SKIP_BLANK_CHECK` positionally on `uv-slot` policy (§6.7) |
| `chip_test.py:2626-2672` | `_dispatch_read` sampling + escalation (§6.6) |
| `chip_test.py:1319-1331` | `_aggregate_cycle_results` stops summing `duration_s` (RPT-D1) |
| `chip_test.py:2604-2622` | `_dispatch_id` records the detected id structurally |
| `chip_test.py:3232-3241`, `cli_handlers.py:2369-2378` | recorded non-claims that R4 falsifies (§5.3) |
| `serial_comm.py:485-490`, `:500-505` | one increment each, beside the existing warning |
| `diagnostic_report.py:48` | `SCHEMA_VERSION` → `"1.8"` |
| `diagnostic_report.py:571-572`, `:638-639` | delete `vpp_mv`/`vpe_mv` |
| `diagnostic_report.py:733`, `:737` | delete the `locked_steps` export (§6.4) |
| `diagnostic_report.py:605-618` | `_transport_dict` reports real counts |
| `diagnostic_report.py:667-729` | `_step_dict` gains fingerprint siblings + `divergence` (additive; `classification` keeps its key) |
| `diagnostic_report.py:771-790` | `to_dict` gains `is_uv` and `elapsed` |
| `diagnostic_report.py:881-894` | remove the render-only `steps total` sum-of-sums |
| `cli_handlers.py:2172-2179` | `_chip_id_fields` reads the structured id |
| `tools/check_devtest_orchestrator.py:152-164` | extend `_HANDLER_FUNCTION_NAMES` (§6.8) |

### Untouched, deliberately

`_dispatch_sdp_leg` (`chip_test.py:3211`) and `_dispatch_sdp` (`:3158`); `derive_plan`'s
purity (I-1); the `plan.steps ↔ results` alignment (I-2); `repeat_policy_tag`
(`:1081`) and `coverage_tag` (`:1106`); the whole firmware repo.

---

## 9. Build order

Dependency-driven, not size-driven. Arrows are hard dependencies.

```
P-A  Blast-radius harness  ──┬─► P-C  Evidence ledger + read-back gate
     fixture corpus (§6.5)   │        (needs the gate to prove nothing moved)
     + dedup byte-identity   │
     assertions (§6.1)       └─► P-F  Report schema 1.8
                                       (needs the same oracle)

P-B  Structural sentinel  ──────► P-C
     predicate + whole-DB sweep      (the sentinel is the LICENCE for the gate;
     (§3.3, RED first)                it must be green BEFORE the gate lands)

P-C  Evidence-gated read-back (R2 corrected: run-level, + synthesized
     passing fingerprint per §6.1)
        │
        └─► P-E  Read-step sampling (R3) — shares the escalation seam and
                 collides with divergence export (§6.6)

P-D  Transport counters (§4)  ──► P-F (transport_health has real data)
                              └─► P-G (a transport-fault investigation has
                                       something to stand on)

P-F  Report fidelity (RPT-A1..E3) — depends on P-A, P-C, P-D
        │
        └─► canonical chip naming (report the matched DB part_number)

P-G  R4 measurement leg (bench) ──► P-H  Session reuse, scoped by the number
     per board class (§5.4)              (may be DEFERRED on the measurement)

P-I  UV FLAG_SKIP_BLANK_CHECK (§6.7) — independent of everything above.
     Its regression test (a UV part holding data outside the target slot)
     must go RED first, and its bench leg is the milestone's one
     irreducible hardware dependency.
```

**Rationale for the three non-obvious orderings:**

1. **P-A before everything.** The milestone names `dedup_fingerprint` byte-identity as its
   blast-radius gate, and §6.1 shows the very first change violates it. The oracle must
   exist and be green before any change that could move the hash. Today no report fixture
   corpus exists in `firestarter_app/tests/fixtures/` at all.
2. **P-B before P-C, RED first.** The read-back gate's safety argument *is* the sentinel
   (`.planning/PROJECT.md:72-77`). Landing the gate first means shipping a change whose
   justification is unproven, and a pre-authored gate leg that was never seen to fail
   proves nothing.
3. **P-D before P-G.** The milestone brief's own framing — "a tool or rig fault is never
   filed as a chip verdict" — depends on the run being able to *say* the link dropped
   frames. Investigating a suspected transport fault with all four counters reading
   `"not measured"` (`diagnostic_report.py:605-618`) is investigating with the instrument
   switched off.

**Parallelisable:** P-B ∥ P-D ∥ P-I after P-A. P-I is fully independent and is the only
leg with a hard bench gate, so it should start early to leave slack for hardware
scheduling.

**Candidate for honest deferral:** P-H. Its payoff is unmeasured, its blast radius is the
largest (§5.3 — the non-fatal-step guarantee), it does not help the sampler's connects at
all (§5.1), and its cheapest sub-step is firmware-side and therefore out of this
milestone's scope.

---

## 10. Open questions this research could not close

| Question | Why it stayed open | Who can close it |
|---|---|---|
| Per-connect cost in seconds, per board class | never measured; `/dev/ttyACM0` was busy during the explore session; likely DTR-reset-dominated on Uno-class | bench leg P-G |
| Basis for `_SUSPECT_THRESHOLD = 5` (`diagnostic_report.py:57`) | chosen while the counters were dormant and never exercised against a real distribution | P-D, once counts exist |
| Whether the whole-DB sweep should also cover user-override DB entries (`~/.firestarter/database.json`) | `derive_plan` reads whatever `db.get_eprom` returns; an override could emit a shape the shipped 746 never do | plan-time decision in P-B |
| Whether `Plan.locked_destructive` itself is deletable (RPT-B2's second half) | live tests depend on it (§6.4) and it feeds `count_applicable`'s `M` | adjudicate in P-F |
| Which of `retries` / `timeouts` are genuinely wireable | `get_response`'s timeout path (`serial_comm.py:552-558`) and `_decode_id_frame` returning `None` are named by RPT-C1 but were not traced end-to-end here | P-D |
| The `firestarter write foo.bin -a 0x3FF00` product bug | firmware half of 999.44, explicitly out of scope (`.planning/PROJECT.md:105-108`) | a later firmware milestone |

---

## Sources

All primary, all read on disk at HEAD (`firestarter_app@0a93999`, meta@`58bb8d80`):

- `firestarter_app/firestarter/chip_test.py` (3539 lines, read in full across sections)
- `firestarter_app/firestarter/diagnostic_report.py` (937 lines, read in full)
- `firestarter_app/firestarter/eprom_operations.py` (§§ `build_flags`, `_operation_context`, `_disconnect_programmer`, `write_eprom`)
- `firestarter_app/firestarter/serial_comm.py` (`_read_and_parse_lines`, `find_and_connect`, `_probe_port`, `__init__`)
- `firestarter_app/firestarter/cli_handlers.py` (`dev_test`, `_make_sampler`, `_chip_id_fields`, `_resolve_write_scope`)
- `firestarter_app/firestarter/hardware.py` (`_sample_one_voltage`, `read_programmer_identity`)
- `firestarter_app/tests/test_chip_test_sdp_leg.py:827-897`; `tests/test_erase_flag_invariants.py:100-161`
- `firestarter_app/tools/check_devtest_orchestrator.py`; `tools/check_diagnostic_report_claims.py`; `tools/parse_devtest_issue.py`
- `firestarter/src/proms/memory.cpp:377-396` (`memory_verify_execute`, early-return on first mismatch)
- `.planning/PROJECT.md` §"Current Milestone: v1.36"; `.planning/ROADMAP.md` §999.36
- `.planning/seeds/dev-test-adaptive-sequencing.md`; `.planning/notes/dev-test-sequence-cost-model.md`
- `.planning/todos/pending/2026-08-30-gate-fingerprint-readback-on-step-failure.md`; `…/2026-08-30-write-init-blank-check-is-whole-device.md`; `…/delete-banner-locked-steps-dead-field.md`
- `.claude/skills/devtest-triage/scripts/devtest_issues.py`; `.claude/skills/devtest-rootcause/scripts/seed_debug_session.py`

Executed (not read): `classify_fingerprint(p, p, repeat_divergent=False)` over a
65536-byte and a 256-byte address-derived pattern — §6.1.

---
*Architecture research for: v1.36 `dev test` fidelity, host-app-only*
*Researched: 2026-09-02*
