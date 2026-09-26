"""Load a deliberately mutated copy of a module under test.

Every mutation guard in this skill's test suite uses this to prove a test can
actually fail: load a copy of the module with one anchor string replaced by a
broken one, then assert the mutant answers the guarded scenario WRONGLY. That
makes the RED demonstration permanent and executable rather than a claim in a
commit message.

The anchor-count assertion is the point of this file. If a later refactor
rewords or removes the anchor string, `source.count(old) == 1` stops holding
and the guard raises loudly instead of silently no-op'ing (patching zero or
several places, or patching the wrong one).

Not collected by `unittest discover` as a test module -- it does not start
with `test_`. Owned jointly by both skills' test suites; kept in this
directory only (`devtest-triage/scripts/tests/`) and imported by
`devtest-rootcause`'s suite is deliberately NOT done -- each skill stays
self-contained, so `devtest-rootcause`'s own test module does not need this
helper (see its SKILL.md and the corresponding plan task).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import types


def load_mutant(module_path: str, old: str, new: str) -> types.ModuleType:
    """Return the module at `module_path` with `old` replaced by `new`.

    Raises `AssertionError` naming the anchor and the actual count when `old`
    does not occur exactly once in the source -- a refactor that dissolves
    the anchor must fail the suite loudly, not silently disarm the guard.
    """
    with open(module_path, encoding="utf-8") as f:
        source = f.read()

    count = source.count(old)
    if count != 1:
        raise AssertionError(
            f"mutation anchor {old!r} occurs {count} time(s) in {module_path}, "
            "expected exactly 1 -- the guard cannot patch a single, unambiguous "
            "location. Update the anchor to match the current source."
        )

    mutated_source = source.replace(old, new, 1)

    tmp_dir = tempfile.mkdtemp(prefix="gsd-mutant-")
    module_name = os.path.splitext(os.path.basename(module_path))[0] + "_mutant"
    mutant_path = os.path.join(tmp_dir, module_name + ".py")
    with open(mutant_path, "w", encoding="utf-8") as f:
        f.write(mutated_source)

    spec = importlib.util.spec_from_file_location(module_name, mutant_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot build an import spec for mutant at {mutant_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
