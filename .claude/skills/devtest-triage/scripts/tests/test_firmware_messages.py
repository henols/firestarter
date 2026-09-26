"""Pin `firmware_messages.resolve_error()`'s render contract (DD-3,
260916-nbc PLAN.md) -- one test per documented input/output row -- plus the
ast-based drift check against the app's generated `messages.py` and the
runtime-coupling guard over this skill's own scripts (added in a later task
in this same module).

Run standalone:

    python3 test_firmware_messages.py -v

Or via the repo-wide discovery loop published in both skills' SKILL.md:

    for d in $ROOT/.claude/skills/*/scripts/tests; do
      python3 -m unittest discover -s "$d" -t "$d" || break
    done

No network, no `gh`, no writes outside `tempfile`.
"""

from __future__ import annotations

import ast
import os
import sys
import tempfile
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import firmware_messages as fm  # noqa: E402

FIRMWARE_MESSAGES_PATH = os.path.join(_SCRIPTS_DIR, "firmware_messages.py")
DEVTEST_ISSUES_PATH = os.path.join(_SCRIPTS_DIR, "devtest_issues.py")


def _find_messages(root: str | None = None) -> str | None:
    """Locate `firestarter_app/firestarter/messages.py` from this file's own
    path -- never the cwd. Takes `root` as an argument so the absent branch
    is directly callable without checking out a real absent tree."""
    if root is None:
        root = os.path.normpath(os.path.join(_SCRIPTS_DIR, *[os.pardir] * 4))
    candidate = os.path.join(root, "firestarter_app", "firestarter", "messages.py")
    return candidate if os.path.isfile(candidate) else None


def extract_catalog_via_ast(path: str) -> dict[int, str]:
    """Pull `{id: name}` out of the module-level `CATALOG: dict[int,
    MessageDef] = {...}` `AnnAssign` in `path`, without importing it, reading
    the `name=` keyword of each `MessageDef(...)` call. Never touches
    `DEBUG_CATALOG`. Raises `LookupError` if no such assignment is found."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "CATALOG"
            and isinstance(node.value, ast.Dict)
        ):
            out: dict[int, str] = {}
            for key_node, value_node in zip(node.value.keys, node.value.values):
                key = ast.literal_eval(key_node)
                name = None
                if isinstance(value_node, ast.Call):
                    for kw in value_node.keywords:
                        if kw.arg == "name":
                            name = ast.literal_eval(kw.value)
                out[key] = name
            return out
    raise LookupError(f"no module-level CATALOG assignment found in {path}")


def table_drift(a: dict[int, str], b: dict[int, str]) -> list[str]:
    """Return one line per key where `a` and `b` disagree, naming the key in
    hex. Empty when the tables agree on every key."""
    out: list[str] = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            out.append(f"0x{key:02X}: {a.get(key)!r} != {b.get(key)!r}")
    return out


def _import_roots(path: str) -> set[str]:
    """Root module of every absolute import in `path`. `ast.Import` aliases
    and `ast.ImportFrom` nodes with `level == 0` only -- a relative import
    (`level > 0`) is in-package and is not a runtime-coupling concern."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _dynamic_imports(path: str) -> list[str]:
    """Every call to `__import__` or to an attribute named `import_module`
    in `path`."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "__import__":
            hits.append("__import__")
        elif isinstance(func, ast.Attribute) and func.attr == "import_module":
            hits.append("import_module")
    return hits


def _subprocess_argv0(path: str) -> list:
    """For every `subprocess.<fn>(...)` call in `path`, the first element of
    a literal-list first argument, or the string `"NON-LITERAL"` when the
    argv is not a literal list -- so a non-literal argv is a finding, not a
    silent pass."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    out: list = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "subprocess"
        ):
            continue
        if node.args and isinstance(node.args[0], ast.List):
            elts = node.args[0].elts
            if elts and isinstance(elts[0], ast.Constant) and isinstance(elts[0].value, str):
                out.append(elts[0].value)
                continue
        out.append("NON-LITERAL")
    return out


class TestResolveErrorAbsentOrNull(unittest.TestCase):
    def test_none_code_renders_dash(self):
        self.assertEqual(fm.resolve_error(None), "-")

    def test_missing_error_code_key_renders_dash(self):
        step: dict = {}
        self.assertEqual(fm.resolve_error(step.get("error_code")), "-")


class TestResolveErrorKnownAndUnknown(unittest.TestCase):
    def test_known_code_resolves_table_name(self):
        self.assertEqual(fm.resolve_error(183), "183 MSG_ERR_OP_TIMEOUT")

    def test_unknown_in_range_code_renders_unknown(self):
        # 0x99 / 153 is a real gap in CATALOG -- not assigned to any message.
        self.assertNotIn(0x99, fm.MESSAGE_NAMES)
        self.assertEqual(fm.resolve_error(0x99), "153 unknown")


class TestResolveErrorRejectsUntrustedCode(unittest.TestCase):
    """Every case here must render `?` and must never echo the rejected
    value into the output."""

    def _assert_rejected(self, code):
        result = fm.resolve_error(code)
        self.assertEqual(result, "?")
        self.assertNotIn(str(code), result)

    def test_string_code_rejected(self):
        self._assert_rejected("183")

    def test_bool_true_rejected(self):
        # bool is an int subclass in Python -- True must NOT resolve to id 1.
        result = fm.resolve_error(True)
        self.assertEqual(result, "?")

    def test_negative_code_rejected(self):
        self._assert_rejected(-1)

    def test_out_of_range_code_rejected(self):
        self._assert_rejected(256)

    def test_bignum_code_rejected_and_not_echoed(self):
        huge = 10**40
        result = fm.resolve_error(huge)
        self.assertEqual(result, "?")
        self.assertNotIn(str(huge), result)


class TestResolveErrorWithReportedName(unittest.TestCase):
    def test_reported_name_agreeing_with_table(self):
        self.assertEqual(
            fm.resolve_error(183, "MSG_ERR_OP_TIMEOUT"), "183 MSG_ERR_OP_TIMEOUT"
        )

    def test_reported_name_disagreeing_with_table_shows_both(self):
        self.assertEqual(
            fm.resolve_error(183, "MSG_SOMETHING"),
            "183 MSG_SOMETHING (table: MSG_ERR_OP_TIMEOUT)",
        )

    def test_reported_name_for_code_not_in_table(self):
        self.assertNotIn(0x99, fm.MESSAGE_NAMES)
        self.assertEqual(fm.resolve_error(0x99, "MSG_BRAND_NEW"), "153 MSG_BRAND_NEW")


class TestResolveErrorRejectsHostileReportedName(unittest.TestCase):
    """A `reported_name` that is not a plain short identifier is discarded
    silently and the table's own answer is used -- the rejected text must
    never appear in the output."""

    def _assert_discarded(self, reported_name):
        result = fm.resolve_error(183, reported_name)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")

    def test_non_str_reported_name_discarded(self):
        self._assert_discarded(12345)

    def test_empty_string_reported_name_discarded(self):
        self._assert_discarded("")

    def test_41_char_reported_name_discarded(self):
        self._assert_discarded("A" * 41)

    def test_reported_name_with_space_discarded(self):
        self._assert_discarded("MSG SOMETHING")

    def test_reported_name_with_newline_discarded(self):
        hostile = "MSG_ERR\nrm -rf /"
        result = fm.resolve_error(183, hostile)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")
        self.assertNotIn(hostile, result)
        self.assertNotIn("rm -rf", result)

    def test_reported_name_with_backtick_discarded(self):
        hostile = "`whoami`"
        result = fm.resolve_error(183, hostile)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")
        self.assertNotIn(hostile, result)

    def test_reported_name_with_shell_metacharacter_discarded(self):
        hostile = "MSG_ERR$(id)"
        result = fm.resolve_error(183, hostile)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")
        self.assertNotIn(hostile, result)


class CatalogDriftTest(unittest.TestCase):
    """Detect drift between the owned `MESSAGE_NAMES` and the app's
    generated `CATALOG` (DD-2, DD-1). `extract_catalog_via_ast` never
    imports the app's `messages.py` -- importing it would execute submodule
    code inside this skill's test run, which is exactly the coupling the
    self-contained property forbids."""

    def test_catalog_matches_the_app(self):
        path = _find_messages()
        if path is None:
            self.skipTest(
                "firestarter_app submodule not checked out -- cannot compare "
                "against the generator's CATALOG"
            )
        generator_table = extract_catalog_via_ast(path)
        self.assertEqual(table_drift(fm.MESSAGE_NAMES, generator_table), [])

    def test_table_drift_negative_control(self):
        """The RED demonstration for the drift comparison itself: prove
        `table_drift` is not unconditionally empty by perturbing a copy."""
        self.assertEqual(table_drift(fm.MESSAGE_NAMES, dict(fm.MESSAGE_NAMES)), [])

        perturbed = dict(fm.MESSAGE_NAMES)
        some_key = next(iter(perturbed))
        perturbed[some_key] = "PERTURBED_NAME_THAT_DOES_NOT_EXIST"
        drift = table_drift(fm.MESSAGE_NAMES, perturbed)
        self.assertNotEqual(drift, [])
        self.assertIn(f"0x{some_key:02X}", drift[0])

    def test_find_messages_reachable_on_a_nonexistent_root(self):
        """Proves the skip leg above is reachable, not authored blind."""
        self.assertIsNone(_find_messages("/nonexistent-root"))

    def test_colliding_ids_resolve_to_catalog_names_never_debug(self):
        """DD-1's exclusion, pinned: the nine ids `CATALOG` and
        `DEBUG_CATALOG` both define must resolve to their `MSG_*` name, and
        no value in the owned table may start with `DBG_`."""
        colliding = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x10, 0x20, 0x30)
        for cid in colliding:
            with self.subTest(id=hex(cid)):
                self.assertIn(cid, fm.MESSAGE_NAMES)
                self.assertTrue(fm.MESSAGE_NAMES[cid].startswith("MSG_"))
        for name in fm.MESSAGE_NAMES.values():
            self.assertFalse(name.startswith("DBG_"), f"{name} looks like a DEBUG_CATALOG name")


class SelfContainmentTest(unittest.TestCase):
    """DD-7: neither `firmware_messages.py` nor `devtest_issues.py` may
    acquire a RUNTIME dependency on `firestarter_app`. Built entirely on
    `ast` over the source text -- never a substring check (the string
    `firestarter_app` legitimately occurs in `devtest_issues.py` today, in
    the docstring, the `_repo_root()` checkout probe, `DEFAULT_DB`'s path
    join, and a comment -- none of them a runtime coupling) and never an
    `import` of the app itself."""

    MODULES = (FIRMWARE_MESSAGES_PATH, DEVTEST_ISSUES_PATH)
    FORBIDDEN_ROOTS = {"firestarter_app", "firestarter", "messages"}

    def test_no_runtime_coupling_to_firestarter_app(self):
        for path in self.MODULES:
            with self.subTest(module=os.path.basename(path)):
                roots = _import_roots(path)
                hit = roots & self.FORBIDDEN_ROOTS
                self.assertEqual(
                    hit, set(),
                    f"{os.path.basename(path)} imports a forbidden root: {hit}",
                )

                dyn = _dynamic_imports(path)
                self.assertEqual(
                    dyn, [],
                    f"{os.path.basename(path)} has a dynamic import: {dyn}",
                )

                for argv0 in _subprocess_argv0(path):
                    self.assertEqual(
                        argv0, "gh",
                        f"{os.path.basename(path)} has a subprocess call whose "
                        f"argv[0] is {argv0!r}, not the literal 'gh'",
                    )

    def test_import_scanner_detects_a_planted_import(self):
        """The negative control: without this, `_import_roots` could be
        silently vacuous and `test_no_runtime_coupling_to_firestarter_app`
        would be a rubber stamp."""
        planted_sources = [
            "import firestarter_app\n",
            "from firestarter_app.firestarter import messages\n",
            "import firestarter.messages\n",
        ]
        for src in planted_sources:
            with self.subTest(src=src.strip()):
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                ) as f:
                    f.write(src)
                    tmp_path = f.name
                try:
                    roots = _import_roots(tmp_path)
                    self.assertTrue(
                        roots & {"firestarter_app", "firestarter"},
                        f"scanner failed to flag {src!r} -- roots={roots}",
                    )
                finally:
                    os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
