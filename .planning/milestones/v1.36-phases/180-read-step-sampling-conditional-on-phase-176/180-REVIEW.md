---
phase: 180-read-step-sampling-conditional-on-phase-176
reviewed: 2026-09-08T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_readback_inventory.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 180: Code Review Report

**Reviewed:** 2026-09-08T00:00:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

This is an incremental review of Phase 180's gap-closure wave (plans 180-04 and 180-05),
scoped against the prior review at `41a264c2` (gitlink `93a1672`, 0 critical / 2 warning /
2 info). The diff under review runs `93a1672..04fd982` in the `firestarter_app` submodule
and touches only these two test files: the IN-02 `_alternating_read_side_effect` factor-out
in `test_chip_test.py`, and the WR-01/WR-02 hardening plus a follow-up mypy narrowing fix in
`test_readback_inventory.py`.

**IN-01 (stale line citation)** is confirmed closed: the docstring on
`test_read_verdict_expression_reads_only_the_last_full_read_result` no longer cites a line
number for the sibling behavioural tests, removing the drift risk entirely rather than just
correcting it.

**IN-02 (duplicated read-side-effect closures)** is confirmed closed: both
`test_read_step_last_run_failure_yields_bad` and
`test_read_step_first_run_failure_with_passing_last_run_yields_ok` now call the shared
`_alternating_read_side_effect(*call_returns)` helper (`test_chip_test.py:1474-1494`), and I
verified the refactor is behaviour-preserving (same call-count-modulo indexing, same
64-zero-byte payload, same two orderings passed at each call site) and both tests still pass.

**WR-01 (one-connect pin only checked the `with` header)** is substantively closed. The
hardened `_read_eprom_connect_shape` now additionally counts every `ast.Call` anywhere in
`read_eprom`'s body whose `func.attr` is `_operation_context`, `_setup_operation`, or
`find_and_connect` (`connect_route_calls`), scoped correctly to `read_eprom`'s own
`FunctionDef` rather than the module (avoiding the false-positive on `_operation_context`'s
own internal `_setup_operation` call that the prior review's naive fix suggestion would have
tripped). I re-derived the anti-vacuity leg by hand (planting a direct
`self._setup_operation(...)` call outside the `with` header) and confirmed against the real
`eprom_operations.py` source that `connect_route_calls` goes from 1 to 2 and the pin's own
equality assertion reddens, exactly as claimed.

**WR-02 (verdict-source pin didn't trace `last_ok` reassignment)** is largely closed for the
mutation shape the prior review's counter-example used (a plain single-target reassignment
statement), but the fix introduces a new, narrower gap of the same kind — see WR-01 below
(renumbered for this review, since this is a fresh finding raised by the hardening itself,
not a residual of the original WR-02).

No hardcoded secrets, dangerous functions, or empty catch blocks were found. All 174 tests in
these two files pass (`pytest tests/test_chip_test.py tests/test_readback_inventory.py -o
addopts=""`), `ruff check` and `ruff format --check` are clean on both files, and the app's
mypy watermark gate is confirmed at exactly 35/35 under Python 3.11 with neither file
contributing an error (consistent with the 180-05 fix commit's own claim).

## Warnings

### WR-01: `_last_ok_assignment_shape`'s "closed claim" is false for multi-target and tuple-unpacking reassignment

**File:** `firestarter_app/tests/test_readback_inventory.py:401-435` (docstring claim at
407-414, vulnerable guard at 425, consuming pin at 176-200, anti-vacuity leg at 470-492)
**Issue:** The docstring for `_last_ok_assignment_shape` states plainly: *"`other` is what
makes the list a closed claim: any third assignment, any augmented assignment and any
walrus on `last_ok` changes the list and reddens a pin asserting it."* This claim is false.
The target-extraction loop only recognizes a plain `ast.Assign` when it has exactly one
target (`len(n.targets) == 1`) and that target is a bare `ast.Name`:

```python
if isinstance(n, ast.Assign) and len(n.targets) == 1:
    target = n.targets[0]
```

A chained assignment (`last_ok = _junk = last_ok and not divergence`) or a tuple-unpacking
assignment (`last_ok, _junk = (last_ok and not divergence), None`) reassigns `last_ok` to
exactly the same divergence-dependent value the WR-02 anti-vacuity leg plants, but neither
form is captured by the loop at all — `target` stays `None` for that node, so it is silently
dropped from `targets` rather than being tagged `"other"`. I verified this empirically
against the real `_dispatch_read` source: with either mutation applied,
`_last_ok_assignment_shape(mutant)["tags"]` still returns exactly
`["const_true", "read_eprom_call"]` (the "everything is fine" shape), and
`_verdict_expression_names(mutant)` is unaffected too (`["VERDICT_BAD", "VERDICT_OK",
"last_ok"]`) — so **both** the pre-hardening and the hardened pin stay green while `last_ok`
now silently depends on `divergence`, the exact regression class Phase 180's WR-02 was
supposed to close for good. This reopens (in a narrower but still ordinary-Python-idiom
form) the same gap the phase's own hardening pass was written to eliminate, and the
docstring's "closed claim" language overclaims what the code actually proves — exactly the
failure mode the review scope calls out ("An over-claiming docstring on a structural pin is
a real defect here, not a style nit").
**Fix:** Flatten every `Assign` target (handling `ast.Tuple`/`ast.List` targets and multiple
plain targets) before checking for `last_ok`, and tag any occurrence found inside a
multi-target or destructuring assignment as `"other"` (never `"const_true"`/`"read_eprom_call"`,
since those two tags should only ever apply to the two known-good single-target forms):

```python
def _flatten_targets(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, (ast.Tuple, ast.List)):
        out: list[ast.AST] = []
        for elt in node.elts:
            out.extend(_flatten_targets(elt))
        return out
    return [node]

for n in ast.walk(fn):
    raw_targets: list[ast.AST] = []
    is_simple_single_target = False
    if isinstance(n, ast.Assign):
        for t in n.targets:
            raw_targets.extend(_flatten_targets(t))
        is_simple_single_target = len(n.targets) == 1 and isinstance(
            n.targets[0], ast.Name
        )
    elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
        raw_targets = [n.target]
        is_simple_single_target = True
    hits_last_ok = any(
        isinstance(t, ast.Name) and t.id == "last_ok" for t in raw_targets
    )
    if hits_last_ok:
        targets.append((n.lineno, n.col_offset, n, is_simple_single_target))
```

and have `_tag` force `"other"` whenever `is_simple_single_target` is `False`, before
applying the existing `const_true`/`read_eprom_call` pattern checks. Add a seventh
anti-vacuity leg planting one of the two forms above (I used
`last_ok = _junk = last_ok and not divergence`) and asserting the hardened pin now reddens
on it.

---

_Reviewed: 2026-09-08T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
