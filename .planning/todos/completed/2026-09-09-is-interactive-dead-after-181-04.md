---
created: 2026-09-09
source: 181-REVIEW.md WR-01
resolves_phase: 185
severity: warning
---

# `_is_interactive` is dead code, and two tests claim a TTY they never simulate

Phase 181 plan 04 deleted `_resolve_write_scope` and, with it, the
`interactive = _is_interactive()` call site in `cli_handlers.dev_test`. The
function itself survived at `firestarter/cli_handlers.py:2299`.

**Measured, not asserted.** An AST scan over `firestarter/` and `tools/` finds
one definition and **zero** call sites. At the phase base `04fd982` the same
scan found a live call at `cli_handlers.py:2401`. So this phase created the
dead code.

## Why it is more than tidy-up

`tests/test_dev_test_cmd.py` still patches it in ~14 places via the `_off_tty()`
helper (`:518-520`), and two tests in `TestUVWriteHasNoPrompt` patch it with
`return_value=True`:

- `test_uv_part_writes_one_slot_on_a_tty` (`:836`, patch at `:843`)
- `test_non_uv_part_is_still_written_in_full_without_a_prompt` (`:862`, patch at `:871`)

Patching a function nothing calls controls nothing. What actually decides the
off-TTY path is `submit_report`'s own `sys.stdin.isatty()` check — and
`CliRunner` is always non-TTY — so **neither test simulates an interactive
terminal despite its name and docstring saying so**. They pass, but not for the
reason they claim.

That is the fail-open shape phase 181's own prohibitions forbid: "a gate must
not read green while the rule it guards is violated."

The `_off_tty()` uses are benign by accident (they force a state `CliRunner`
already produces), but they are equally inert.

## What a fix has to cover

1. Either delete `_is_interactive` or restore a real caller.
2. If deleted, remove `"_is_interactive"` from `_HANDLER_FUNCTION_NAMES` in
   `tools/check_devtest_orchestrator.py:163` — that gate asserts every listed
   name resolves to a real callable, so it will go red otherwise.
3. Rework the ~14 `_off_tty()` sites (`:572, 613, 645, 675, 764, 781, 856, 911,
   950, 967, 994` and the helper itself).
4. Make the two `on_a_tty` tests genuinely simulate a TTY — patch what the code
   actually reads (`sys.stdin.isatty`, or `submit_report`'s seam) — or rename
   them and their docstrings to state what they really cover.

## Why it was not fixed in phase 181

Found by the phase's own code-review gate, which is advisory and does not block.
The fix spans ~14 call sites plus the allow-list, which is a scoped piece of
work rather than a close-time touch-up. Recorded here instead of expanding a
completed phase's scope unasked.
