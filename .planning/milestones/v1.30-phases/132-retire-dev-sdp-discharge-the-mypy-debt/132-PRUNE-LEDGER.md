# Phase 132 Plan 03 — Prune Ledger: `test_dev_sdp_cmd.py` → `test_sdp_honesty.py`

**Purpose (D-04):** a ~550-line deletion inside a `git mv` is exactly the diff shape that hides
a real loss. RETIRE-03 protects four honesty assertions out of 558 lines; "no net loss" is
defensible only if it is a *measured* claim about those four assertions **plus** an accounted
loss for everything else. This ledger makes that loss legible to a reader who was not here.

**Source commits (submodule `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`):**
- `7495c9e` — the rename + gate target-list edit + docstring citation fixes (RETIRE-02, D-03).
- `3dddfe3` — task 2: the four survivors retargeted onto `firestarter/sdp_honesty.py`, plus the
  new import-purity test. This commit also removed every test function that drove the retired
  `dev sdp` subcommand through Click's test harness (surface shape, gate ordering, consent
  matrix, no-port-opened, tblc-warn, exit-code contract), because their mere presence would have
  kept `CliRunner` imported and referenced in a module whose whole point is to no longer drive
  a CLI surface.
- `6d561a0` — task 3: the local `make_app_context` factory, the `_off_tty`/`_on_tty` context
  managers, and every now-dead chip-name constant removed.

---

## 1. What survived

| Test function | Pre-move line (`test_dev_sdp_cmd.py`) | Keys on (assertion literals) | New SUT |
|---|---|---|---|
| `test_summary_line_carries_the_unreadable_state_caveat_on_both_directions` | `:395` | `"cannot be read back"` in both the `enable` and `disable` output | `firestarter.sdp_honesty.emission_summary("enable"\|"disable", chip)` |
| `test_summary_line_carries_no_duration_figure` | `:423` | `not re.search(r"\d+\s*(us\|µs\|ms\|s)\b", summary_line, re.IGNORECASE)` | `firestarter.sdp_honesty.emission_summary("enable", chip)` |
| `test_no_fabricated_lock_state_boolean_in_the_report` | `:453` | `"was emitted"`, `"cannot be read back"`, `"not a claim about the chip's actual state"` | `firestarter.sdp_honesty.emission_summary("enable", chip)` |
| `test_firmware_too_old_is_reported_when_unknown_cmd_comes_back` | `:513` | `"firestarter fw --install"`, plus (`"outdated"` or `"does not implement"`) | `firestarter.sdp_honesty.map_unknown_cmd_to_outdated(exc, mode, chip)` |

All four survive under their **original, byte-identical names**, keyed on their **original
assertion literals**. None was weakened into a source-string-presence check (D-01's explicit
rejection).

**One test added, not a survivor:** `test_sdp_honesty_module_imports_only_leaf_firestarter_modules`
— an AST-based import-purity test enforcing `sdp_honesty.py`'s own declared invariant
(top-level imports ⊆ `{"__future__", "firestarter.exceptions", "firestarter.messages"}`, no
`click`). Proven non-vacuous during plan 132-03 task 2 by a planted top-level `import click` in
`sdp_honesty.py`, run to a verbatim `AssertionError` naming `click` as the extra item, then
reverted (see `132-03-SUMMARY.md` for the captured failure text).

---

## 2. What was pruned

| Name | Pre-move line | What it asserted | Disposition |
|---|---|---|---|
| `test_surface_is_chip_then_mode_with_a_yes_flag` | `:125` | `dev sdp --help`'s locked surface shape (chip-then-mode, `-y` present, no destructive flag) | gate dies with the command |
| `test_gate_order_absent_chip_refuses_before_confirm_and_before_serial` | `:151` | an absent chip refuses at Gate 1, before confirm/serial | gate dies with the command |
| `test_gate_order_capability_refusal_refuses_before_confirm_and_before_serial` (2 parametrized cases: FRAM, pre-SDP DIP24_2816) | `:182` | capability-refused chips refuse at Gate 2, before confirm/serial | covered elsewhere — `tests/test_check_sdp_capability.py` + `tests/test_sdp_db_invariant.py` (the 43/41/84 partition and its non-vacuity) |
| `test_adapter_required_part_hears_the_capability_reason_not_the_adapter_reason` (9 parametrized cases, all `_ADAPTER_REQUIRED_CHIPS`) | `:208` | the capability-before-support-status **ordering** on all nine adapter-required 0x0D parts | gate dies with the command — see §4, this one is the load-bearing loss, not merely dead code |
| `test_non_0x0d_chip_is_refused_with_the_wrong_protocol_reason` | `:235` | a non-0x0D chip refuses with the wrong-protocol reason | gate dies with the command |
| `test_consent_matrix` (4 parametrized cases: tty+yes, tty+no, off-tty+no-yes, off-tty+yes) | `:275` | the four-cell TTY/`-y` consent matrix, including the off-TTY refusal | gate dies with the command |
| `test_enable_and_disable_share_one_gate_with_different_text` | `:328` | the confirm prompt's wording differs by direction | gate dies with the command |
| `test_no_port_opened_on_any_refusal_with_a_real_operator` | `:369` | a real `EpromOperator`'s transport is never touched on refusal | gate dies with the command |
| `test_tblc_warn_prints_at_warning_and_exit_code_stays_zero` | `:479` | a `MSG_WARN_SDP_TBLC_EXCEEDED` frame prints at WARNING without changing exit code | gate dies with the command |
| `test_success_exit_zero_and_failure_exit_one` | `:539` | the binary exit-code contract (0 on ok, 1 on not-ok) | gate dies with the command |
| `make_app_context` (factory) | `:80` | n/a (test fixture helper) | gate dies with the command — its only callers were the ten pruned test functions above |
| `runner` fixture | `:105-107` | n/a (test fixture helper) | gate dies with the command — its only purpose was invoking `cli` via `CliRunner` |
| `_off_tty` / `_on_tty` (context managers) | `:110`, `:115` | n/a (test fixture helpers) | gate dies with the command — patched `_is_interactive`, which only the TTY-consent tests exercised |
| `_ABSENT_CHIP` | `:54` | n/a (constant) | gate dies with the command |
| `_FRAM_CHIP` | `:56` | n/a (constant) | covered elsewhere — capability-refusal coverage moved to `tests/test_check_sdp_capability.py` |
| `_PRESDP_DIP2816_CHIP` | `:58` | n/a (constant) | covered elsewhere — same as `_FRAM_CHIP` |
| `_NON_0X0D_CHIP` | `:60` | n/a (constant) | gate dies with the command |
| `_ADAPTER_REQUIRED_CHIPS` (9-element list) | `:67-77` | n/a (constant) | gate dies with the command — see §4 for the ordering-proof loss this list's only consumer carried |

Every row above carries a disposition of either `gate dies with the command` or `covered
elsewhere` naming a file (and, where applicable, the specific gate) that already provides the
coverage. 18 rows total (10 test functions/parametrizations, 8 helpers/constants).

---

## 3. Counts

| Metric | Value | Command that produced it |
|---|---|---|
| Tests collected before the move | **26** | `python -m pytest tests/test_dev_sdp_cmd.py -q --collect-only` (run during plan 132-02; independently reconstructed here as 14 base `def test_*` functions + 1 extra case from the 2-way `capability_refusal` parametrize + 8 extra from the 9-way `adapter_required` parametrize + 3 extra from the 4-way `consent_matrix` parametrize = 14 + 1 + 8 + 3 = 26) |
| Tests collected after the move (before retarget, end of task 1) | **26** | unchanged — task 1 only renamed the file and edited the gate/docstrings, no test content changed |
| Tests collected after the retarget (end of task 2) | **5** | `python -m pytest tests/test_sdp_honesty.py -q --collect-only` |
| Tests collected after the prune (end of task 3, final) | **5** | `python -m pytest tests/test_sdp_honesty.py -q --collect-only` — task 3 pruned helpers/constants only, no test functions (task 2 already removed every non-survivor test) |
| Number pruned (test cases) | **21** | 26 − 5 = 21 |
| Number retargeted (survivors, unchanged names) | **4** | §1 |
| Number newly added | **1** | `test_sdp_honesty_module_imports_only_leaf_firestarter_modules` |
| File line count before | **558** | `git show 7495c9e^:tests/test_dev_sdp_cmd.py \| wc -l` |
| File line count after | **197** | `wc -l < tests/test_sdp_honesty.py` |

Arithmetic check: 4 survivors + 1 new = 5 tests collected after — matches the independently
measured collected count above.

---

## 4. The accounted loss

Stated plainly, without hedging, separating losses of coverage for code that **still exists**
from losses of coverage for code **being deleted in plan 132-04**:

1. **The capability-before-support-status ordering proof
   (`test_adapter_required_part_hears_the_capability_reason_not_the_adapter_reason`, all nine
   adapter-required 0x0D parts).** This proved that when a part is both capability-refused *and*
   adapter-required, the user hears "this part has no SDP" rather than "get an adapter" — a
   real behavioural ordering inside `dev_sdp`'s gate sequence (Gate 2 before Gate 3). **This is a
   loss of coverage for code being deleted in plan 132-04** — the gate sequence itself (Gate 1
   through Gate 4 in `cli_handlers.py`'s `dev_sdp` span) is retired along with the subcommand,
   so there is no surviving code left for this ordering to be asserted against. It is not
   re-provable elsewhere because `sdp_capability()`'s predicate alone (still covered by
   `tests/test_check_sdp_capability.py` and `tests/test_sdp_db_invariant.py`) does not encode
   *which gate runs first* — only whether a given part is capability-allowed. D-04 explicitly
   forbids re-authoring this ordering onto `sdp_capability()` directly, since that would be
   duplicate coverage dressed as preservation of a property that no longer has a subject.

2. **The off-TTY refusal behaviour (`test_consent_matrix`'s `off_tty_no_yes` cell, and the
   TTY-branch tests generally).** This proved that `dev_sdp` refuses to proceed off a TTY
   without `-y`/`--yes` — the mere absence of a TTY does not stand in for consent. **This is a
   loss of coverage for code being deleted in plan 132-04** — `_is_interactive()`'s call site
   inside `dev_sdp` and the `Confirm.ask`/TTY-refusal gates are part of the deleted span; no
   other subcommand's consent gate depends on this specific proof.

3. **The binary exit-code contract (`test_success_exit_zero_and_failure_exit_one`).** This
   proved `dev_sdp` returns exit 0 on success and exit 1 on failure, with no tri-state
   introduced. **This is a loss of coverage for code being deleted in plan 132-04** — the exit
   code is emitted by `dev_sdp`'s own `sys.exit(...)` call, which is deleted with the rest of the
   span.

4. **The fact that the four survivors now pin wording rather than delivery.** Before this
   phase, the four honesty assertions were exercised end-to-end through `click.testing.CliRunner`
   and `click.echo`, proving the wording actually reaches a captured console output. After this
   phase, the same four assertions call `firestarter/sdp_honesty.py`'s functions directly — a
   real SUT, but one with no `click` dependency and no console-delivery path of its own.
   **This is a loss of coverage for code that still exists, but the loss was already taken and
   already recorded, not newly introduced by this plan.** Plan 132-02 captured the one-time
   delivery-path proof (the unmodified 26-test suite passing against the rewired `dev_sdp`,
   recorded in `132-MYPY-LEDGER.md` §1a) *before* this plan's move made that proof unrepeatable.
   D-05 states the residual explicitly: between this phase and Phase 134 (the wording's next
   intended caller), the caveat has no user-reachable carrier at all. This plan does not create
   that gap; it inherits it, having taken the one available chance to prove the gap's edges.

5. **The capability-refusal reason-text legs
   (`test_gate_order_capability_refusal_refuses_before_confirm_and_before_serial`, FRAM and
   pre-SDP DIP24_2816).** These proved a capability-refused chip is refused with the correct
   reason text, before any confirm/serial call. **This is coverage for code that still exists**
   (`sdp_capability()` itself is not being deleted) **but it is not a real reduction** — the
   capability partition and its non-vacuity are already fully covered by
   `tests/test_sdp_db_invariant.py` (the 43/41/84 partition gate, seven named tests) and
   `tests/test_check_sdp_capability.py` (the capability-predicate gate tests). D-04 names this
   pair explicitly as the case where re-authoring onto `sdp_capability()` would be duplicate
   coverage dressed as preservation — so pruning here, unlike items 1-3, discharges no unique
   proof.

---

## 5. Why "no net loss" is defensible

- **The four honesty assertions survive, under their original names, keyed on their original
  literals, and are measured to pass** (`python -m pytest tests/test_sdp_honesty.py -q` — 5
  passed, 0 failed; see `132-03-SUMMARY.md` for the full run).
- **The capability partition and its non-vacuity are covered by Phase 131's gate**
  (`tests/test_sdp_db_invariant.py`'s 43/41/84 partition tests) and by
  `tests/test_check_sdp_capability.py` — independent of anything this module ever tested, so
  pruning the capability-refusal reason-text legs (§4 item 5) discharges no unique coverage.
- **The three losses in §4 that concern code being deleted (items 1-3) are named here, not
  discovered later.** Each is a real behavioural proof that dies because its subject dies —
  stated plainly, with the specific gate sequence and file each depended on, rather than
  silently absorbed into a 361-line reduction (558 → 197) inside a `git mv`.
- **The one loss that concerns still-existing code (§4 item 4, the wording-vs-delivery gap) was
  already taken deliberately, in plan 132-02, before this plan's move made the delivery-path
  proof unrepeatable** — the gap is inherited and recorded, not newly introduced.

"No net loss" is therefore not a bare assertion: it is the four-assertion survival measured in
§1 and §3, plus the explicit, itemized accounting of everything else in §2 and §4 — with the
real reductions (items 1-3) named separately from the non-reductions (items 4-5).
