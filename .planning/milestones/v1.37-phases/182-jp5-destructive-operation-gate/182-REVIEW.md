---
phase: 182-jp5-destructive-operation-gate
reviewed: 2026-09-10T21:08:53Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - firestarter_app/firestarter/jp5_gate.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/ic_layout.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/data/pinouts.json
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/diff_db.py
  - firestarter_app/tests/test_jp5_gate.py
  - firestarter_app/tests/test_ic_layout.py
  - firestarter_app/tests/test_build_db_inclusion.py
  - firestarter_app/tests/test_revision_constants_parity.py
  - firestarter_app/tests/test_wire_dict_equivalence.py
  - firestarter_app/tests/test_diff_db_gate.py
  - firestarter_app/tests/golden/wire_dict_expected_deltas_182.json
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 182: Code Review Report

**Reviewed:** 2026-09-10T21:08:53Z
**Depth:** standard
**Files Reviewed:** 16
**Status:** issues_found

## Summary

Phase 182 adds a socket-pin-1 (JP5/A19) destructive-operation gate: `jp5_gate.py` (pure policy),
two new wiring points in `cli_handlers.py` (`write`/`erase` only), a `pin1_hazard_acknowledged`
parameter on `EpromOperator.write_eprom`/`erase_eprom`, a new `Pin1HazardRefusedError`, a
`DIP32_27C801` pinout entry, a `resolve_pinout_key` fork in `build_db.py`, and a matching
root-cause rule in `diff_db.py`.

I traced the gate end to end against the real shipped `chip_database.json` (746 rows) rather than
trusting the tests' framing, and ran the phase's test files directly (`pytest
tests/test_jp5_gate.py tests/test_ic_layout.py tests/test_build_db_inclusion.py
tests/test_revision_constants_parity.py tests/test_wire_dict_equivalence.py
tests/test_diff_db_gate.py` — all 112 pass). The core safety properties hold and are backed by
tests that exercise the real data, not just synthetic fixtures:

- No TTY → `confirm_fn` is never called and the operation is refused (`confirm_or_refuse`'s
  off-tty branch runs before `Confirm.ask` is reached).
- `-f/--force` neither satisfies nor bypasses the gate (`test_cli_erase_with_force_on_affected_part_still_refuses_off_tty`).
- Scope is exactly `write`/`erase` — `read`/`verify`/`blank`/`id` never call into `jp5_gate` at all.
- The affected-part set is derived, not hand-listed: over the real DB, exactly `DIP32_27C801`
  (8 rows: AM27C080, AM27LV080, AT27C080, M27C801×2, MX27C8000, MX27C8000A, UPD27C8001) is
  flagged, and `DIP32_SST39SF040` (A18, one bit short) is correctly excluded — verified myself by
  re-running `_derived_sets`-equivalent logic over `chip_database.json`.
- `build_db.py`'s `variant_lo` fork stays correctly scoped inside `proto_id == 0x08`; the four
  protocol-0x10 variant_lo values (0x10–0x13) fall through to `DIP32_STD` unmodified, and the
  `_PGM_ON_PIN31_MAX_SIZE` size-threshold fall-through still protects SST37VF040-class 512K parts
  from being misrouted onto `DIP32_27C020`'s PGM-on-pin-31 layout.
- `diff_db.py`'s `RULE_PHASE182_A19_PINOUT` is correctly value- and part-number-scoped and the
  live `tools/diff_db.py` run explains exactly 8 chips with that label.

I did find two real gaps in how completely the gate's CLI-facing behavior was integrated, both in
the fail-*safe* direction (over-refusal / silent non-integration), not a bypass — see below.

## Warnings

### WR-01: `confirm_or_refuse` and `require_acknowledged` disagree about a chip with no resolvable `bus-config`, and the mismatch produces an unescapable, misleadingly-worded refusal unrelated to JP5

**File:** `firestarter_app/firestarter/jp5_gate.py:41-66` (CLI layer) vs `firestarter_app/firestarter/jp5_gate.py:83-106` (operator layer), wired from `firestarter_app/firestarter/cli_handlers.py:753` and `:873`

**Issue:** The two gate layers use different fail modes for the same input (`bus_config` with no
`"bus"` key at all, e.g. `None` or `{}`):

- `is_affected()` (used by the CLI's `confirm_or_refuse`) calls `socket_pin1_address_bit`, which
  returns `None` for a falsy `bus_config` — so `is_affected(None)` is `False`, and
  `confirm_or_refuse(chip, None, "write")` returns `True` **immediately, with no hazard text
  printed and no prompt shown** (its own docstring: "Returns True immediately when ... the part is
  not affected -- no hazard text is printed on that path").
- `require_acknowledged()` (used inside `EpromOperator.write_eprom`/`erase_eprom`) treats the same
  input oppositely: `if not bus_config or not bus_config.get("bus"): raise
  Pin1HazardRefusedError(...)` — **unconditionally, regardless of the `acknowledged` value**. This
  is by its own docstring deliberate ("fail-closed, because absent evidence cannot prove socket
  pin 1 is safe"), confirmed by `test_require_acknowledged_no_bus_key_raises_fail_closed` and
  `test_require_acknowledged_fails_closed_through_a_real_unknown_pinout_lookup`.

Net effect for a chip whose `bus-config` fails to resolve: the CLI's `confirm_or_refuse` silently
decides "not affected" (no warning to the operator, `pin1_hazard_acknowledged=True` is then passed
unconditionally per `cli_handlers.py:772`/`:881`), and then `require_acknowledged` inside
`write_eprom`/`erase_eprom` raises anyway — but with the generic "no bus configuration is
available to prove socket pin 1 is safe" message, not the JP5-specific `hazard_text`, and with
**no possible escape**: no prompt was ever shown, so there is no "answer yes" path, and `-f`
already doesn't help by design. This means *any* chip whose `bus-config` can't be resolved —
which is structurally possible today: `resolve_pinout_key` in `build_db.py` can return a key that
is not a member of `VALID_PINOUT_KEYS` and `main()` only prints a `WARN:` to stderr in that case
(`tools/build_db.py:279-280`), it does **not** skip the row — would have `write`/`erase`
permanently refused, misattributed to a JP5/A19 hazard it has nothing to do with.

I confirmed this is not reachable by any of the 746 rows in the currently-shipped
`chip_database.json` (every `pinout` value resolves against `pinouts.json`'s 16 keys), so this is
a latent inconsistency rather than a live regression — but it is a real defect in the gate's own
layered design that a future DB regen (a typo'd new pinout key, or a maintainer adding a pinout
branch to `resolve_pinout_key`/`classify` without also adding the corresponding entry to
`pinouts.json`) would trip silently, with the resulting bug report looking like a JP5/A19 problem
on a chip that has no relationship to A19 at all.

**Fix:** Make the two layers agree. Either:
1. Have `confirm_or_refuse` fail the same way `require_acknowledged` does for "no evidence at
   all" (print a distinct "cannot determine socket pin 1 safety" message and refuse, the same way
   the off-TTY path refuses), so the CLI-visible behavior matches the operator-layer contract; or
2. Route both layers through one shared classification helper (e.g. an
   `Affected | NotAffected | Unknown` return from `socket_pin1_address_bit`/`is_affected`) so
   "missing evidence" is a single, deliberately-chosen policy applied identically by
   `confirm_or_refuse` and `require_acknowledged`, instead of the current two independent readings
   of the same falsy-`bus_config` input.

### WR-02: `dev write-cycle` silently inherits the new fail-closed default with no gate integration and no test coverage

**File:** `firestarter_app/firestarter/eprom_operations.py:1147-1255` (`write_cycle_eprom`), wired from `firestarter_app/firestarter/cli_handlers.py:1551-1597` (`dev_write_cycle`)

**Issue:** `write_cycle_eprom` calls `self.erase_eprom(eprom_name, eprom_data_dict,
operation_flags)` and `self.write_eprom(eprom_name, eprom_data_dict, source_image_path,
operation_flags)` (eprom_operations.py:1185, :1190) without passing `pin1_hazard_acknowledged`, so
both silently take the new default of `False`. `cli_handlers.dev_write_cycle` (the `dev
write-cycle` command, a pre-existing bench diagnostic that erases, writes, and read-back-verifies
N cycles) never calls `jp5_gate.confirm_or_refuse` before invoking it, unlike the top-level
`write`/`erase` commands.

The result is directionally safe (the 8 JP5-hazard chips are unconditionally refused, never
silently written), but it is an unreviewed side effect of this phase rather than a deliberate
scope decision: `dev write-cycle` is now **permanently unusable** on those 8 chips, with no way
for a bench operator who has physically inspected/cut JP5 to proceed (no CLI prompt is ever shown,
and `-f/--force` was never wired to this parameter). There is also no test anywhere in the suite
(`tests/test_jp5_gate.py` or elsewhere) that exercises this interaction, so this behavior change
was not verified either way.

**Fix:** Either wire `jp5_gate.confirm_or_refuse` into `dev_write_cycle` (and any other CLI path
that reaches `write_eprom`/`erase_eprom`) the same way `write()`/`erase()` do, so a bench operator
gets the same confirm-or-refuse UX, or explicitly document/test that `dev write-cycle` is
out-of-scope-and-permanently-blocked for JP5-affected parts, so this isn't rediscovered as a bug
report later.

## Info

### IN-01: No end-to-end test exercises the TTY-accept path through the CLI into the operator layer

**File:** `firestarter_app/tests/test_jp5_gate.py`

**Issue:** The test suite thoroughly covers the off-TTY refusal path end-to-end via `CliRunner`
(`test_cli_erase_with_force_on_affected_part_still_refuses_off_tty`), and covers
`confirm_or_refuse`'s TTY-accept return value in isolation (`test_confirm_or_refuse_tty_accept_returns_true`),
and covers `write_eprom`/`erase_eprom` honoring `pin1_hazard_acknowledged=True` in isolation
(`test_erase_eprom_acknowledged_reaches_operation_context`) — but no single test drives the full
chain (CLI `write`/`erase` command, with a mocked TTY-accept `confirm_fn`, asserting
`eprom_operator.write_eprom`/`erase_eprom` is actually invoked with
`pin1_hazard_acknowledged=True`). This is the one path where the two hardcoded `True` literals at
`cli_handlers.py:772` and `:881` could silently stop being reached (e.g. if a future refactor
reordered the `confirm_or_refuse` call after the operator call) without any test catching it.

**Fix:** Add a `CliRunner` test that mocks `confirm_fn`/`isatty_fn` to simulate an operator
answering "yes", and asserts `eprom_operator.write_eprom`/`erase_eprom` (a `Mock(spec=
EpromOperator)`, as `test_cli_erase_with_force_on_affected_part_still_refuses_off_tty` already
does) is called with `pin1_hazard_acknowledged=True`.

---

_Reviewed: 2026-09-10T21:08:53Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
