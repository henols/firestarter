---
phase: 260807-kaq
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/tests/test_chip_test_blank_check_order.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_chip_test_sdp_leg.py
autonomous: true
requirements: [QBC-01, QBC-02, QBC-03]
must_haves:
  truths:
    - "On an erasable part with an executable erase step, `dev test` runs blank-check AFTER erase, so a chip that merely held data no longer scores a failure verdict."
    - "On a part whose family auto-erases on write and therefore has no erase step (protocol 0x05, 0x0D), blank-check is emitted NA instead of a guaranteed-BAD supported step."
    - "UV-EPROM plans keep their pre-write blank-check at its current position, unchanged."
    - "`write_scope=\"none\"` plans are byte-for-byte unchanged in step list and locked_destructive."
    - "SRAM/FRAM still short-circuit to supported=False with today's reason string."
    - "A `dev test` run on an erasable chip whose device is not blank until erase has run exits 0, not 1."
  artifacts:
    - path: "firestarter_app/firestarter/chip_test.py"
      provides: "conditional blank-check placement in derive_plan + truthful step-order comment"
      contains: "_AUTO_ERASE_ON_WRITE_PROTOCOLS"
    - path: "firestarter_app/tests/test_chip_test_blank_check_order.py"
      provides: "unit-level ordering proof across all four placement cases"
      min_lines: 60
  key_links:
    - from: "firestarter/chip_test.py::derive_plan erase arm"
      to: "firestarter/chip_test.py::derive_plan blank-check placement"
      via: "a single boolean set where the supported erase Step is appended"
      pattern: "erase_is_executable"
    - from: "tests/test_dev_test_cmd.py"
      to: "firestarter/cli_handlers.py::_dev_test_exit_code"
      via: "CliRunner end-to-end exit-code assertion"
      pattern: "result.exit_code == 0"
---

<objective>
`dev test` currently emits `OP_BLANK_CHECK` as step 3 of every plan — before any
write, and before the erase step that is appended LAST among the destructive ops.
On an electrically erasable part the chip still holds data at that point, so
`check_eprom_blank` returns False, the step scores `VERDICT_BAD`, and the run
exits 1 (BAD is the most-severe code in `_EXIT_CODE_PRECEDENCE`). A community
tester is told their chip is faulty for being in exactly the state the sweep
expects it to be in.

Purpose: make blank-check's verdict mean "the tool works" rather than "this
device happened to be blank when you plugged it in", without weakening the one
case where a pre-write blank-check is genuinely actionable (UV-EPROM, where the
write is irrecoverable and only UV light can erase).

Output: a conditional placement rule in `derive_plan`, a truthful step-order
comment, and two RED-first proofs (unit ordering + end-to-end exit code).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<repo_topology>
The code change lands in the **`firestarter_app` submodule**, already checked out
on branch `fix/dev-test-blank-check-after-erase` (forked from `origin/beta`).

- ALL code commits happen inside `/workspaces/firestarter_app`, on that branch.
  Use `git -C /workspaces/firestarter_app ...` — the shell cwd resets between calls.
- Do **NOT** stage the submodule gitlink in the meta repo. `/workspaces` is on a
  v1.30 branch staged for a PR; only `.planning/` artifacts belong there.
- Test invocation (the doubled `-q` in `addopts` suppresses the count line):
  `cd /workspaces/firestarter_app && python -m pytest -o addopts="" -q`
- Gates: `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`.
</repo_topology>

<context>
@/workspaces/firestarter_app/firestarter/chip_test.py
@/workspaces/firestarter_app/tests/test_chip_test.py
@/workspaces/firestarter_app/tests/test_dev_test_cmd.py
</context>

<measured_ground_truth>
Verified against HEAD of `fix/dev-test-blank-check-after-erase` before this plan
was written. Re-confirm cheaply; do not re-derive from scratch.

**Current `derive_plan` emission order** (`firestarter/chip_test.py:575-766`):
`OP_ID` (581) → `OP_READ` (587) → `OP_BLANK_CHECK` (593-605) →
`OP_WRITE`/`OP_WRITE_PARTIAL` (614-628, `write_execute` only) →
`OP_VERIFY` (638-645, `write_execute` only) →
`OP_ERASE` (651-682; **supported** only when `can_erase and protocol !=
_PROTOCOL_FLASH4` **and** `write_execute`, otherwise an NA step with a
family-fact reason) → the six-step SDP leg, appended as a contiguous block at
the very end (694-758).

**Verdict path:** `_dispatch_step` (`chip_test.py:1601-1605`) maps
`check_eprom_blank() is False` → `VERDICT_BAD`. `_VERDICT_EXIT_CODES`
(`cli_handlers.py:2008-2014`) maps `VERDICT_BAD → 1`, and
`_EXIT_CODE_PRECEDENCE = (1, 2, 0)` (`cli_handlers.py:2026-2042`) makes BAD the
**most severe** code — so this defect produces exit 1, the worst outcome the
command can report. (Note the D-14 correction: exit precedence is an explicit
most-severe-first walk, NOT the numeric `max`; `dev_test`'s own docstring at
`cli_handlers.py:2401-2403` still says "computed as max over per-step exit
codes" and is stale. Out of scope here — record it, do not fix it.)

**Constants already in the module:** `_PROTOCOL_FLASH4 = 0x05` (line 304) and
`_PROTOCOL_EEPROM_28C` (0x0D, referenced at line 663). `is_uv` is already
computed at line 556 and is documented as the only complete-and-exact UV axis
(301/301).

**Fixture chips with ready-made constants** in `tests/test_dev_test_cmd.py`:
`_CHIP_NO_ID = "M8720"` (protocol 0x08, EEPROM, `FLAG_CAN_ERASE` set — the
established erasable fixture, gets a real erase step), `_CHIP_UV = "AM27512"`,
`_CHIP_ALLOW = "AT28C256"` (protocol 0x0D — the auto-erase-on-write case, and
also an SDP ALLOW chip so its plan carries the six-step SDP leg).

**Order-sensitive assertions that may move** (update, never delete):
`tests/test_chip_test.py:666` (`nd_ops == [OP_ID, OP_READ, OP_BLANK_CHECK]`,
`write_scope="none"`), `tests/test_chip_test.py:674-675`
(`index(OP_VERIFY)` between write and erase),
`tests/test_chip_test_sdp_leg.py:2103` (`== ["id", "read", "blank-check"]`,
`write_scope="none"`). Under the rule below, all three are **predicted to stay
green** — the `"none"` plans are untouched and verify still precedes erase.
Measure; do not assume either way.

**Existing in-repo precedent for the fix's direction:** the shipped `erase`
command already carries `-b/--blank-check  Do a blank check after erase.`
(`tests/__snapshots__/test_characterization.ambr:165`).
</measured_ground_truth>

<placement_rule>
The rule is conditional, not a blanket move. Applied in `derive_plan`, in this
precedence order:

1. **SRAM/FRAM** (`etype in _SRAM_FRAM_ETYPES or protocol in _SRAM_PROTO_IDS`) —
   unchanged in every respect: NA step, today's reason string, today's position.
2. **An executable erase step exists in this plan** (the supported `OP_ERASE`
   append at line 653 actually ran) — blank-check moves to immediately AFTER
   that erase step, and before the SDP leg block. It is now a real assertion
   with a deterministic expected outcome, and doubles as erase's own oracle.
3. **`write_execute` and `protocol in _AUTO_ERASE_ON_WRITE_PROTOCOLS`** (a new
   module constant = `frozenset({_PROTOCOL_FLASH4, _PROTOCOL_EEPROM_28C})`,
   i.e. 0x05 and 0x0D) — blank-check stays at its current position but is
   emitted `supported=False` with a family-fact reason. **Rationale, to be
   written into the source comment:** no step in this plan can leave the device
   blank (each page write auto-erases internally; there is no erase op to sit
   behind), so a supported blank-check here is guaranteed to report chip state
   rather than tool health — the same defect wearing a different hat. NA is the
   honest verdict, it contributes exit 0, and `count_applicable` already
   excludes NA slots from M (see the comment at `chip_test.py:2211`).
4. **Everything else** — unchanged, at today's position, with today's
   `supported`/`reason`. This deliberately covers: UV-EPROM at any scope (a
   pre-write blank-check is genuinely actionable there — the write is
   irrecoverable and only UV light erases, so "not blank" is a real
   operator-actionable finding, not a false failure); every `write_scope="none"`
   plan (nothing writes, so reporting chip state is the whole point, and that
   scope is unreachable from `dev test` since Phase 121); and any non-UV part
   with the erase flag clear that is NOT on 0x05/0x0D.

**Why case 3 is narrowed to a measured protocol set rather than the broader
"non-UV with no erase step":** the broad predicate would also swallow any
one-time-programmable / PROM-like part in the database, for which "not blank
before write" is a genuine pre-write fault that must stay visible. Task 1
measures whether such parts exist. The narrow set is strictly safer and, if the
measurement shows the bucket is exactly {0x05, 0x0D}, the two rules coincide.
</placement_rule>

<tasks>

<task type="auto">
  <name>Task 1: Measure the affected chip population and confirm the verdict path</name>
  <files>/tmp/claude-1000/-workspaces/0af9ac8d-e2a4-476d-93b2-a3b77d7219be/scratchpad/kaq_buckets.py (throwaway, NOT committed)</files>
  <action>
Write a throwaway script under the scratchpad that imports `EpromDatabase` the
same way `tests/test_chip_test.py`'s `_REAL_DB` fixture does, walks every chip in
`firestarter/data/chip_database.json`, and calls `derive_plan(name, db,
write_scope="full")` — or, if that is too slow across the whole DB, replicates
`derive_plan`'s three input reads only (`convert_to_programmer` for `flags` and
`algorithm`, `full["electrical-type"]`, `is_uv_eprom(full)`).

Partition every chip into exactly four buckets and print the counts plus the
total, asserting the four sum to the DB total:
  (A) executable erase step present (`can_erase and protocol != 0x05`) — case 2
  (B) `is_uv` true — case 4/UV
  (C) not A, not B, and `protocol in {0x05, 0x0D}` — case 3, the NA candidates
  (D) not A, not B, not C — the residual that MUST keep today's behavior

For bucket C and bucket D separately, print the distinct
`(electrical-type, protocol, can_erase)` tuples and up to five example chip
names per tuple. Bucket D is the load-bearing measurement: it answers whether
any OTP/PROM-like part would have been swallowed by the broader predicate.

Separately confirm the verdict path by reading, not running: quote the two live
lines proving `check_eprom_blank() is False` reaches exit 1 —
`chip_test.py:1601-1605` (`VERDICT_BAD`) and `cli_handlers.py:2008-2014` +
`:2029` (`VERDICT_BAD -> 1`, and 1 is first in `_EXIT_CODE_PRECEDENCE`). Record
that BAD is the MOST severe code, so this defect produces the worst exit the
command can emit — and record that `dev_test`'s docstring at
`cli_handlers.py:2401-2403` still describes the superseded `max` mechanism (a
known-stale line, NOT this plan's scope to fix).

Do not commit the script. Its output is the evidence Task 2 quotes verbatim in
the new source comment and the SUMMARY records.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app &amp;&amp; python /tmp/claude-1000/-workspaces/0af9ac8d-e2a4-476d-93b2-a3b77d7219be/scratchpad/kaq_buckets.py</automated>
  </verify>
  <done>
Four bucket counts printed and proven to sum to the DB total. Bucket C's and
bucket D's distinct `(electrical-type, protocol, can_erase)` tuples enumerated
with example chip names. An explicit written statement of whether bucket D
contains any part for which a pre-write blank-check is genuinely actionable —
and therefore whether the narrow `{0x05, 0x0D}` predicate and the broad
"non-UV, no erase step" predicate coincide or differ, and by how many chips.
The BAD-outranks-marginal exit path confirmed by citation with line numbers.
No file committed by this task.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: RED-first proofs, then the conditional placement in derive_plan</name>
  <files>/workspaces/firestarter_app/tests/test_chip_test_blank_check_order.py, /workspaces/firestarter_app/tests/test_dev_test_cmd.py, /workspaces/firestarter_app/firestarter/chip_test.py</files>
  <behavior>
Unit legs, new module `tests/test_chip_test_blank_check_order.py` (import
`derive_plan` and the `OP_*` names from `firestarter.chip_test`, and build the
real DB the same way `tests/test_chip_test.py`'s `_REAL_DB` does):
  - M8720, `write_scope="full"`: `ops.index(OP_BLANK_CHECK) > ops.index(OP_ERASE)`
    AND the blank-check step is `supported=True` AND every SDP-leg op still has a
    strictly greater index than blank-check (the leg stays a contiguous terminal
    block).
  - M8720, `write_scope="none"`: `[s.op for s in plan.steps] ==
    [OP_ID, OP_READ, OP_BLANK_CHECK]` and `locked_destructive` op set is
    exactly `{"write", "verify", "erase"}` — the untouched-scope proof.
  - AM27512 (UV), `write_scope="full"`: blank-check index is still 2, still
    `supported=True` — the UV-unchanged proof.
  - AT28C256 (protocol 0x0D), `write_scope="full"`: blank-check index is still 2
    but `supported is False`, and its `reason` names the family fact (protocol
    0x0D / 28C family, each page write auto-erases internally) — NOT the flag
    name `FLAG_CAN_ERASE`, matching the wording precedent the erase arm already
    set at `chip_test.py:671-674`.
  - A non-vacuity leg: assert M8720's plan contains exactly one `OP_BLANK_CHECK`
    step and exactly one `OP_ERASE` step, so the index comparison above cannot
    pass by accident on a duplicated op.

End-to-end leg, appended to `tests/test_dev_test_cmd.py` using the existing
`CliRunner` + `make_app_context` + `make_hardware_manager` harness (see
`test_non_uv_part_is_written_in_full_without_a_prompt` at line 529 for the exact
invocation shape, and note the autouse `FIRESTARTER_CONFIG_DIR` fixture):
  - Build a `make_clean_operator()` and then override `check_eprom_blank` with a
    closure that returns `operator.erase_eprom.called` — an honest simulation of
    a used erasable device that only becomes blank once erase has actually run.
    Invoke `dev test M8720`. Assert `result.exit_code == 0` and that the
    persisted report's `blank-check` step verdict is `OK`. **This leg fails on
    the current ordering for exactly the right reason** (blank-check runs first,
    `erase_eprom.called` is False, verdict BAD, exit 1).
  - A second leg: `dev test AT28C256` with `check_eprom_blank.return_value =
    False`. Assert `result.exit_code == 0`, that the report's `blank-check`
    verdict is `NA`, and that `operator.check_eprom_blank` was never called at
    all (an unsupported step is skipped, never dispatched).
  </behavior>
  <action>
Write the tests FIRST and observe them RED against the unmodified
`chip_test.py`. Capture the failure output verbatim for the SUMMARY — a test
that has not been seen to fail proves nothing.

Then implement the rule in `derive_plan`:

Add a module-level `_AUTO_ERASE_ON_WRITE_PROTOCOLS = frozenset({_PROTOCOL_FLASH4,
_PROTOCOL_EEPROM_28C})` next to the existing protocol constants, with a comment
citing the measured bucket-C population from Task 1.

Restructure the blank-check emission (currently `chip_test.py:589-605`) to BUILD
the `Step` into a local variable instead of appending it, keeping the SRAM/FRAM
short-circuit branch byte-identical in its condition and reason string. In the
erase arm, set a single boolean where the supported erase `Step` is appended
(line 653) — name it `erase_is_executable` — so the placement decision and the
erase decision can never drift apart; do not re-derive the predicate a second
time at the blank-check site.

Append the blank-check step per the four-case rule in `<placement_rule>`: after
the erase step when `erase_is_executable`, otherwise at its original position,
with case 3 flipping `supported` to False and substituting the family-fact
reason. The SDP leg block must remain contiguous and terminal in every case.

Update the two comments that would otherwise lie:
  - the blank-check comment at `chip_test.py:589-592` — it currently describes
    only the SRAM/FRAM decision and implies a fixed position;
  - the verify comment at `chip_test.py:630-637`, which states the destructive
    order `(write, verify, erase)` is deliberate and positioned so. That order
    is UNCHANGED by this plan, so the sentence stays true — but add the new fact
    that a blank-check may now follow the erase step, and why.
Both comments must name the reason a blank-check is only meaningful once
something in the plan can leave the device blank.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app &amp;&amp; python -m pytest -o addopts="" -q tests/test_chip_test_blank_check_order.py tests/test_dev_test_cmd.py</automated>
  </verify>
  <done>
Both RED observations captured verbatim before any edit to `chip_test.py`. All
new legs green afterwards. `derive_plan` contains exactly one predicate deciding
whether an erase step is executable, consumed by both the erase arm and the
blank-check placement. Both stale-risk comments updated so neither misdescribes
the emitted order. SRAM/FRAM condition and reason string unchanged.
  </done>
</task>

<task type="auto">
  <name>Task 3: Full-suite reconciliation, gates, and submodule commit</name>
  <files>/workspaces/firestarter_app/tests/test_chip_test.py, /workspaces/firestarter_app/tests/test_chip_test_sdp_leg.py</files>
  <action>
Run the full suite and reconcile every failure against the rule — updating
expectations, never deleting assertions.

Expected-and-must-be-checked consequences:
  - `tests/test_chip_test.py:666` and `tests/test_chip_test_sdp_leg.py:2103` are
    both `write_scope="none"` assertions and are PREDICTED to stay green;
    `tests/test_chip_test.py:675` (`verify` before `erase`) is likewise
    predicted green since the destructive triple's relative order is untouched.
    If any of the three actually moves, that is a finding — record what moved
    and why before changing it.
  - AT28C256 (and any other 0x05/0x0D chip) now emits an NA blank-check, so
    `count_applicable`'s M drops by one for those chips. Any test pinning an
    N-of-M figure or a step-verdict map for an ALLOW-chip run will move. Record
    the M delta explicitly in the SUMMARY — do not let a banner number change
    silently.
  - Any report-shape or snapshot test that reads the ordered `steps` list for an
    erasable chip will see blank-check in a new slot. Re-baseline only after
    confirming the new order matches the rule.

Then run the gates and commit inside the submodule, on branch
`fix/dev-test-blank-check-after-erase`. Do NOT stage the submodule gitlink in
the meta repo — confirm with `git -C /workspaces status --short` that the
`firestarter_app` gitlink is not staged before finishing.

Record in the SUMMARY: the before/after full-suite pass counts, the exact list
of tests whose expectations were updated with the one-line reason for each, the
M delta, and the fact that this fix is verified only against mocked operators —
no silicon was exercised, so the erase-then-blank-check sequence remains
unproven on real hardware and is the natural next bench check.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app &amp;&amp; python -m pytest -o addopts="" -q &amp;&amp; ruff check firestarter/ tests/ &amp;&amp; ruff format --check firestarter/ tests/</automated>
  </verify>
  <done>
Full suite green with a pass count at least the pre-change baseline plus the new
legs. Both ruff gates exit 0. Every updated assertion has a recorded one-line
reason. Commits exist inside `/workspaces/firestarter_app` on
`fix/dev-test-blank-check-after-erase`; `git -C /workspaces status --short`
shows no staged gitlink for the submodule.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| host CLI → chip socket | `dev test` issues destructive writes and erases to physical silicon; step ORDER is the only thing standing between a plan and an unrecoverable write |
| community tester → issue tracker | a false BAD verdict becomes a filed hardware-fault report about a healthy chip |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-kaq-01 | Tampering | `derive_plan` erase/blank-check ordering | mitigate | a single `erase_is_executable` boolean feeds both arms, so the placement rule can never drift from the erase decision; the write/verify/erase triple's relative order is asserted unchanged by `test_chip_test.py:674-675` |
| T-kaq-02 | Repudiation | UV-EPROM plans | mitigate | case 4 leaves the pre-write blank-check exactly where it is; an irrecoverable UV write is still preceded by the blank reading that warrants it, proven by the AM27512 leg |
| T-kaq-03 | Information disclosure | NA blank-check reason string | accept | the reason names a public family fact (protocol 0x0D auto-erases per page), no host or device secret |
| T-kaq-04 | Denial of service | `count_applicable` M shrinking for 0x05/0x0D | mitigate | Task 3 requires the M delta to be measured and recorded rather than absorbed silently, so the N-of-M banner's meaning stays auditable |
| T-kaq-SC | Tampering | npm/pip/cargo installs | mitigate | this plan installs NOTHING — no new dependency in any task; if any task finds itself needing one, stop and escalate rather than install |
</threat_model>

<verification>
1. `derive_plan("M8720", db, write_scope="full")` places blank-check after erase
   and before the SDP leg.
2. `derive_plan("AM27512", db, write_scope="full")` is unchanged.
3. `derive_plan("AT28C256", db, write_scope="full")` emits an NA blank-check at
   index 2 with a family-fact reason.
4. Every `write_scope="none"` plan is unchanged in both `steps` and
   `locked_destructive`.
5. A `dev test M8720` run whose device only becomes blank after erase exits 0.
6. A `dev test AT28C256` run with a non-blank device exits 0 and never calls
   `check_eprom_blank`.
7. Full suite green; both ruff gates exit 0.
</verification>

<success_criteria>
- Blank-check no longer produces a BAD verdict for a chip in its expected state,
  on either the has-erase-step path or the auto-erase-on-write path.
- No regression to UV-EPROM, SRAM/FRAM, or `write_scope="none"` behavior.
- Both fixes proven RED-first, with the failure output captured verbatim.
- Every comment describing step order in `chip_test.py` is true after the change.
- Honest limits recorded: mocked operators only, no silicon.
</success_criteria>

<output>
Create `/workspaces/.planning/quick/260807-kaq-dev-test-blank-check-must-run-after-eras/260807-kaq-SUMMARY.md` when done.
</output>
</content>
</invoke>
