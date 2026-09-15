"""RED/GREEN coverage for `survey_provenance.py`'s corpus detector.

WHY THIS FILE EXISTS (v1.33 post-close finding, 2026-08-24)
-----------------------------------------------------------
`survey_provenance.py` was the SWEEP-03 / SWEEP-06 oracle for Phase 154 and it
shipped with **no test file at all**. Its detector regex is

    (//|/\\*|^\\s*\\*|#)\\s*(Task|Phase|Plan|P\\d{3}|Req|REQ-|CAP-0|D-\\d|WR-\\d|LOOP-\\d|\\d{3}-CONTEXT)

which anchors the token immediately after the comment opener. Two whole classes
of GSD provenance are therefore invisible to it:

  1. **Mid-line tokens.** `# needed (D-02).` and `* ... NOT measured -- Phase 145
     may record the real figure` both carry provenance the sweep was supposed to
     triage, and neither matches.
  2. **Requirement families not on the fixed list.** Only `REQ-`, `CAP-0`, `D-\\d`,
     `WR-\\d` and `LOOP-\\d` are named. The project has **96** requirement family
     prefixes; `SWEEP-`, `SUB-`, `RPT-`, `DEVTEST-`, `TABLE-` and 88 others were
     never counted.

Measured consequence: SWEEP-03's discharge text claims `D-#` hit lines in
`firestarter/{src,include}` went `34 across 9 files -> 4 across 1 file`. Under
the anchored regex that reproduces exactly (4). Mid-line aware it is **87 across
21 files** -- the headline evidence was an artifact of where the regex anchored,
not a measurement of the property SWEEP-03 states.

Python docstrings are in scope too: `chip_test.py:537` is
`\"\"\"Ordered, derived test plan for a single chip (SWEEP-01).` -- shipped prose
carrying a requirement ID, invisible to a detector that only looks for `#`.

CONTRACT UNDER TEST
-------------------
- The corrected detector finds provenance tokens ANYWHERE inside comment or
  docstring context, never only at the comment opener.
- It never fires on provenance-shaped text in live CODE (a string literal that
  is not a docstring, an identifier, a dict key).
- `--legacy-anchored` reproduces the historical anchored numbers byte for byte,
  so every figure already recorded in `.planning/` stays reproducible.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_TOOL = _HERE / "survey_provenance.py"


def _run(fw: Path, app: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_TOOL), str(fw), str(app), *extra],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def repos(tmp_path: Path):
    """A minimal two-repo corpus with one file per group the tool scans."""
    fw = tmp_path / "fw"
    app = tmp_path / "app"
    for d in ("src", "include", "test", "lib"):
        (fw / d).mkdir(parents=True)
    for d in ("firestarter", "tests", "tools"):
        (app / d).mkdir(parents=True)
    # Keep every group non-empty so the "silence is never success" guard and the
    # explicit-group emptiness guard are never what a test is measuring.
    (fw / "lib" / "filler.c").write_text("// Phase 1 anchored filler\n", encoding="utf-8")
    (fw / "test" / "filler.cpp").write_text("// Phase 2 anchored filler\n", encoding="utf-8")
    (app / "tests" / "filler.py").write_text("# Phase 3 anchored filler\n", encoding="utf-8")
    (app / "tools" / "filler.py").write_text("# Phase 4 anchored filler\n", encoding="utf-8")
    (fw / "include" / "filler.h").write_text("// Phase 5 anchored filler\n", encoding="utf-8")
    return fw, app


def _hits(fw: Path, app: Path, group: str, *extra: str) -> int:
    """Hit count for one group.

    The tool exits 2 with "silence is never success" when the WHOLE selected
    scope produces zero hits. For a single-group selection that is precisely
    "this group has 0 hits", so it is translated rather than treated as an
    error -- otherwise no must-not-fire case could ever be expressed.
    """
    import json

    proc = _run(fw, app, "--group", group, "--json", *extra)
    if proc.returncode == 2 and "silence is never success" in proc.stderr:
        return 0
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)[group]["hits"]


# ---------------------------------------------------------------------------
# 1. Mid-line tokens in comment context -- the primary miss.
# ---------------------------------------------------------------------------


def test_midline_d_token_in_c_line_comment_is_a_hit(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text("int x = 1;  // needed (D-02).\n", encoding="utf-8")
    assert _hits(fw, app, "fw-src") == 1


def test_midline_phase_in_block_comment_continuation_is_a_hit(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text(
        "/*\n * an [ASSUMED] figure; NOT measured -- Phase 145 may record the real one\n */\n",
        encoding="utf-8",
    )
    assert _hits(fw, app, "fw-src") == 1


def test_midline_token_in_python_comment_is_a_hit(repos):
    fw, app = repos
    (app / "firestarter" / "a.py").write_text(
        "y = 2  # id-check: ALWAYS first (SWEEP-03). Supported only when the chip\n",
        encoding="utf-8",
    )
    assert _hits(fw, app, "app-pkg") == 1


# ---------------------------------------------------------------------------
# 2. Requirement families beyond the fixed list.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("token", ["SWEEP-01", "SUB-03", "RPT-04", "DEVTEST-05", "TABLE-02"])
def test_unlisted_requirement_families_are_hits(repos, token):
    fw, app = repos
    (app / "firestarter" / "a.py").write_text(f"# Dedup fingerprint ({token})\n", encoding="utf-8")
    assert _hits(fw, app, "app-pkg") == 1


# ---------------------------------------------------------------------------
# 3. Python docstrings are shipped prose and count.
# ---------------------------------------------------------------------------


def test_docstring_requirement_id_is_a_hit(repos):
    fw, app = repos
    (app / "firestarter" / "a.py").write_text(
        'def plan():\n    """Ordered, derived test plan for a single chip (SWEEP-01)."""\n    return 1\n',
        encoding="utf-8",
    )
    assert _hits(fw, app, "app-pkg") == 1


# ---------------------------------------------------------------------------
# 4. Fail-closed: provenance-shaped text in CODE must never fire.
# ---------------------------------------------------------------------------


def test_identifier_named_like_a_token_is_not_a_hit(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text(
        "int Phase145_counter = 0;\nconst char *k = \"D-02\";\n", encoding="utf-8"
    )
    assert _hits(fw, app, "fw-src") == 0


def test_non_docstring_string_literal_is_not_a_hit(repos):
    fw, app = repos
    (app / "firestarter" / "a.py").write_text(
        'LABEL = "SWEEP-01"\nd = {"D-02": 1}\n', encoding="utf-8"
    )
    assert _hits(fw, app, "app-pkg") == 0


def test_code_before_a_comment_does_not_swallow_the_code(repos):
    """A token in code on a line that ALSO has an unrelated comment is not a hit."""
    fw, app = repos
    (fw / "src" / "a.cpp").write_text(
        'const char *k = "SWEEP-01";  // ordinary trailing note\n', encoding="utf-8"
    )
    assert _hits(fw, app, "fw-src") == 0


# ---------------------------------------------------------------------------
# 5. The historical anchored view stays reproducible.
# ---------------------------------------------------------------------------


def test_legacy_anchored_mode_misses_what_the_fix_finds(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text("int x = 1;  // needed (D-02).\n", encoding="utf-8")
    assert _hits(fw, app, "fw-src") == 1
    assert _hits(fw, app, "fw-src", "--legacy-anchored") == 0


def test_legacy_anchored_still_finds_anchored_tokens(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text("// Phase 141 Plan 04 -- both refusals\n", encoding="utf-8")
    assert _hits(fw, app, "fw-src", "--legacy-anchored") == 1


# ---------------------------------------------------------------------------
# 6. --assert-tokens-zero must see the widened corpus too.
# ---------------------------------------------------------------------------


def test_assert_tokens_zero_catches_a_midline_violation(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text("int x = 1;  // needed (D-02).\n", encoding="utf-8")
    proc = _run(fw, app, "--group", "fw-src", "--assert-tokens-zero", "D-#")
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_assert_tokens_zero_passes_on_a_clean_group(repos):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text("int x = 1;  // ordinary note\n", encoding="utf-8")
    proc = _run(fw, app, "--group", "fw-lib", "--assert-tokens-zero", "D-#")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_assert_tokens_zero_sees_an_unlisted_family(repos):
    """The widened corpus must be assertable, not merely countable."""
    fw, app = repos
    (app / "firestarter" / "a.py").write_text("# derived plan (SWEEP-01)\n", encoding="utf-8")
    proc = _run(fw, app, "--group", "app-pkg", "--assert-tokens-zero", "REQ-FAMILY")
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_implicit_string_concatenation_is_not_a_docstring(repos):
    """tokenize emits NL for line breaks inside brackets.

    Treating NL as a statement start classified each fragment of an implicitly
    concatenated string literal as a docstring, wrongly counting live code at
    `diff_db.py:175` and `chip_test.py:3827`.
    """
    fw, app = repos
    (app / "firestarter" / "a.py").write_text(
        'MSG = (\n    "first line\\n"\n    " values verbatim (SAFE-04, unmoved);\\n"\n)\n',
        encoding="utf-8",
    )
    assert _hits(fw, app, "app-pkg") == 0


def test_real_docstring_after_the_nl_fix_still_counts(repos):
    fw, app = repos
    (app / "firestarter" / "a.py").write_text(
        '"""Module docstring (SWEEP-01)."""\n\n\ndef f():\n    """Func docstring (D-02)."""\n    return 1\n',
        encoding="utf-8",
    )
    assert _hits(fw, app, "app-pkg") == 2


def test_bare_plan_reference_is_a_hit(repos):
    """`(157-03, DECODE-04)` was only ever detected via DECODE-04."""
    fw, app = repos
    (fw / "src" / "a.cpp").write_text("// clamped at parse time (T-44-01 cap)\n", encoding="utf-8")
    assert _hits(fw, app, "fw-src") == 1


def test_file_line_range_is_not_a_plan_reference(repos):
    """`rurp_shield.h:25-94` is a citation into code, not a plan reference."""
    fw, app = repos
    (fw / "src" / "a.cpp").write_text(
        "// The old #defines in rurp_shield.h:25-94 remain in place\n", encoding="utf-8"
    )
    assert _hits(fw, app, "fw-src") == 0


@pytest.mark.parametrize(
    "line",
    [
        "// Thresholds UNCHANGED - bench measurement (2026-05-26) validated reads\n",
        "// iterations, and an [ASSUMED] ~20-60 us per-pulse overhead adds 15 s\n",
        "// (CMD_READ_VPP..CMD_HW_VERSION occupy 11-15, and slots 9 and 10 were\n",
        "// The old #defines in rurp_shield.h:25-94 remain in place\n",
        '// Operator, 2026-07-31: "No VPP DAC on this board"\n',
    ],
)
def test_dates_ranges_and_line_ranges_are_not_plan_references(repos, line):
    """All five were false positives of a bare \\d{2,3}-\\d{2}, found by sampling."""
    fw, app = repos
    (fw / "src" / "a.cpp").write_text(line, encoding="utf-8")
    assert _hits(fw, app, "fw-src") == 0


@pytest.mark.parametrize(
    "line",
    [
        "// clamped at parse time (T-44-01 cap)\n",
        "// `protection_gate_for_entry` (plan 151-06) returns it\n",
        "// or abort -- plan 142-06 owes the test proving that\n",
        "// fits uint8_t (157-03) */\n",
    ],
)
def test_real_plan_and_task_references_still_hit(repos, line):
    fw, app = repos
    (fw / "src" / "a.cpp").write_text(line, encoding="utf-8")
    assert _hits(fw, app, "fw-src") == 1
