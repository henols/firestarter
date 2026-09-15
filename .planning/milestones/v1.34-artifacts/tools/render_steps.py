#!/usr/bin/env python3
"""render_steps.py -- the SC#3 empty-step-list-diff gate (Phase 160 Plan 06, T-160-40/41/42).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Pure standard-library Python, no third-party imports.

What this measures, and why the empty diff is a measured property and not a tautology
---------------------------------------------------------------------------------------
`PROCEDURE.md`'s `## Step list` section carries no arm-conditional text today -- SC#3's claim
is that the procedure is arm-agnostic. That claim is worth nothing as prose alone; a later
editor could add a step that reads differently for `control` than for `v133` and nothing
would notice. This tool makes the claim a *gate* instead of a sentence.

It renders the step list once per arm and prints one `<step-id>\t<step-text>` line per step,
in document order. The step's substitution tokens (`$ARM_BIN`, `$PORT`, `$CELL_ID`, ...) are
emitted **as the literal token text**, never expanded -- expanding `$ARM_BIN` to one arm's
absolute binary path would make the two renders differ *by construction*, which would defeat
the very property this gate exists to measure. What `--arm` actually selects is *inclusion*:
a step whose heading carries the marker `[arm: control]` is emitted only when `--arm control`
is given, and likewise for `[arm: v133]`; a step with no marker is emitted for both arms, with
no marker text to strip because none was present.

Because the real `PROCEDURE.md` carries zero such markers, `--arm control`'s output and
`--arm v133`'s output are byte-identical today, and `diff`-ing them produces nothing. That
emptiness is the measured fact SC#3 requires -- not an assumption baked into this tool. The
moment a future edit adds one `[arm: ...]`-marked step, the two renders diverge and the diff
goes non-empty; that is the gate doing its job, not a bug. See the `--selftest` positive and
negative legs below, and this plan's SUMMARY.md, for both directions observed live.

A second, independently gated section (Amendment 4, Phase 162)
-----------------------------------------------------------------
`PROCEDURE.md`'s `## Chip-sweep step list` section (`C-01` ... `C-NN`) is a second,
independent step list for the phase-162 chip-sweep shape -- parsed and rendered by exactly
the same machinery, selected with `--section {P,C}`. `--section` **defaults to `P`**, so every
existing invocation -- including `run_gates.sh`'s two current calls -- behaves byte-identically
to before this section existed. The same substitution-token and inclusion-marker semantics
apply verbatim to both sections: a token such as `$ARM_BIN`, `$PORT` or `$CHIP_TOKEN` is
emitted as literal token text, never expanded, and `--arm` selects *inclusion* only via the
`[arm: ...]` marker -- which must appear in neither section's real text. `_NEXT_H2_RE` already
terminates a section at the next `## ` heading, so a `## Chip-sweep step list` heading is
invisible to a `--section P` parse (and a `## Step list` heading is invisible to a `--section
C` parse) -- the two sections cannot bleed into each other. Exactly two hardcoded facts differ
between the sections: the heading text `extract_step_list_section()` looks for, and the
step-id pattern `validate_steps()` enforces (`P-\\d\\d` for `P`, `C-\\d\\d` for `C`). Every
other property -- duplicate-id refusal, strict ascending order, and the arm-annotation domain
check -- is identical and shared.

Fail-closed contract
---------------------
A step-list section that is absent, or present but empty, is refused with a non-zero exit and
a `FAIL:` line -- a renderer that emitted nothing and exited 0 would make the diff trivially
(and meaninglessly) empty, and that exact failure shape has already shipped once in this repo
(T-160-41). This applies identically to section `C`: a missing `## Chip-sweep step list` is a
named refusal, never an empty render with exit 0. Step ids must be unique, must match the
section's own two-digit id pattern (`P-\\d\\d` for section `P`, `C-\\d\\d` for section `C`),
and must appear in strictly ascending numeric order; an annotation value must be one of the two
known arm names. Each violation is a distinct non-zero exit naming the problem.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MILESTONE_DIR = _HERE.parent
_DEFAULT_PROCEDURE = _MILESTONE_DIR / "PROCEDURE.md"

_ARM_CHOICES = ["control", "v133"]
_SECTION_CHOICES = ["P", "C"]

_STEP_LIST_HEADING_RE = re.compile(r"^##\s+Step list\s*$", re.MULTILINE)
_CHIP_STEP_LIST_HEADING_RE = re.compile(r"^##\s+Chip-sweep step list\s*$", re.MULTILINE)
_NEXT_H2_RE = re.compile(r"^##\s+\S.*$", re.MULTILINE)
_STEP_HEADING_RE = re.compile(r"^###\s+(?P<id>\S+)\s*[—\-:]\s*(?P<text>.+?)\s*$")
_STEP_ID_RE = re.compile(r"^P-(?P<num>\d\d)$")
_CHIP_STEP_ID_RE = re.compile(r"^C-(?P<num>\d\d)$")
_ANNOTATION_RE = re.compile(r"\[\s*arm\s*:\s*(?P<arm>[A-Za-z0-9_]+)\s*\]")

# The exactly-two hardcoded facts that differ between sections -- everything else
# (extract_step_list_section's use of _NEXT_H2_RE, parse_steps, render_for_arm,
# the arm-annotation domain check inside validate_steps) is shared and unchanged.
_SECTION_HEADING_RE = {"P": _STEP_LIST_HEADING_RE, "C": _CHIP_STEP_LIST_HEADING_RE}
_SECTION_HEADING_NAME = {"P": "## Step list", "C": "## Chip-sweep step list"}
_SECTION_ID_RE = {"P": _STEP_ID_RE, "C": _CHIP_STEP_ID_RE}
_SECTION_ID_LABEL = {"P": "P-NN", "C": "C-NN"}


class ProcedureParseError(ValueError):
    """Raised for any malformed procedure input -- the fail-closed contract."""


def extract_step_list_section(text: str, section: str = "P") -> str:
    """Return the text strictly between `section`'s own H2 heading and the next '## ' heading.

    `section` is 'P' (the '## Step list' heading, the original and default behaviour) or 'C'
    (the '## Chip-sweep step list' heading, Amendment 4). `_NEXT_H2_RE` terminates the section
    at the next H2 regardless of which section is being extracted, which is exactly what keeps
    the two sections from bleeding into each other.

    Raises ProcedureParseError, naming the missing heading, if it is absent.
    """
    heading_re = _SECTION_HEADING_RE[section]
    heading_name = _SECTION_HEADING_NAME[section]
    m = heading_re.search(text)
    if not m:
        raise ProcedureParseError(f"no {heading_name!r} section found in the procedure")
    start = m.end()
    nxt = _NEXT_H2_RE.search(text, pos=start)
    end = nxt.start() if nxt else len(text)
    return text[start:end]


def parse_steps(section_text: str) -> list[dict]:
    """Parse every '### <id> — <title>' heading in the step-list section, in order, together
    with the full body text that follows it up to the next '### ' heading (or the end of the
    section). The heading's title and the body are flattened onto a single line each -- this
    is deliberate: a step's literal command shape (which carries `$ARM_BIN` and this
    procedure's other substitution tokens) lives in the body, not just the heading, and a
    step's emitted 'imperative text' must carry it so the token is visible in the render
    rather than only in prose no render ever touches.

    Returns a list of {"id": str, "text": str, "arm": str | None} dicts, one per heading, in
    document order. Does NOT validate uniqueness/ordering/annotation domain -- that is
    validate_steps()'s job, kept separate so --selftest can exercise each check in isolation.
    Raises ProcedureParseError if a '### ' line does not match the expected 'id — title'
    shape, or if zero step headings are found at all.
    """
    lines = section_text.splitlines()
    heading_positions: list[tuple[int, re.Match]] = []
    for i, line in enumerate(lines):
        if not line.startswith("###"):
            continue
        m = _STEP_HEADING_RE.match(line)
        if not m:
            raise ProcedureParseError(f"unparseable step heading line: {line!r}")
        heading_positions.append((i, m))

    if not heading_positions:
        raise ProcedureParseError("'## Step list' section contains zero step headings")

    steps: list[dict] = []
    for idx, (line_no, m) in enumerate(heading_positions):
        raw_id = m.group("id")
        body_start = line_no + 1
        body_end = heading_positions[idx + 1][0] if idx + 1 < len(heading_positions) else len(lines)
        body_lines = lines[body_start:body_end]
        combined_raw = m.group("text") + " " + " ".join(body_lines)
        arm_match = _ANNOTATION_RE.search(combined_raw)
        arm = arm_match.group("arm") if arm_match else None
        clean_text = _ANNOTATION_RE.sub("", combined_raw)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        steps.append({"id": raw_id, "text": clean_text, "arm": arm})
    return steps


def validate_steps(steps: list[dict], section: str = "P") -> None:
    """Raise ProcedureParseError on: an id that does not match `section`'s own two-digit id
    pattern (`P-NN` for section 'P', `C-NN` for section 'C'), a duplicate id, ids out of
    ascending numeric order, or an annotation naming an arm outside _ARM_CHOICES. Every check
    beyond the id pattern itself is identical and shared between the two sections.
    """
    id_re = _SECTION_ID_RE[section]
    id_label = _SECTION_ID_LABEL[section]
    seen: set[str] = set()
    prev_num: int | None = None
    for step in steps:
        step_id = step["id"]
        m = id_re.match(step_id)
        if not m:
            raise ProcedureParseError(f"step id {step_id!r} does not match the {id_label} pattern")
        num = int(m.group("num"))
        if step_id in seen:
            raise ProcedureParseError(f"duplicate step id: {step_id!r}")
        seen.add(step_id)
        if prev_num is not None and num <= prev_num:
            raise ProcedureParseError(
                f"step ids are not in strictly ascending order: {step_id!r} follows a step "
                f"numbered {prev_num:02d} or higher"
            )
        prev_num = num
        if step["arm"] is not None and step["arm"] not in _ARM_CHOICES:
            raise ProcedureParseError(
                f"step {step_id!r} carries an unknown arm annotation {step['arm']!r} "
                f"(expected one of {_ARM_CHOICES})"
            )


def render_for_arm(steps: list[dict], arm: str) -> list[str]:
    """Return the '<id>\\t<text>' lines for `arm`, in document order.

    A step with arm=None is included for every arm (its annotation marker, if any, was
    already stripped by parse_steps()). A step with arm=<name> is included only when
    `arm == <name>`. Substitution tokens inside `text` are never touched -- they were never
    expanded by parse_steps() in the first place, so there is nothing to do here beyond
    filtering by inclusion.
    """
    return [f"{s['id']}\t{s['text']}" for s in steps if s["arm"] is None or s["arm"] == arm]


def load_and_render(procedure_path: Path, arm: str, section: str = "P") -> list[str]:
    text = procedure_path.read_text()
    section_text = extract_step_list_section(text, section)
    steps = parse_steps(section_text)
    validate_steps(steps, section)
    return render_for_arm(steps, arm)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

_FIXTURE_HEADER = "# Fixture Procedure\n\n## Scope\n\nirrelevant preamble.\n\n"
_FIXTURE_FOOTER = "\n## Outcome taxonomy\n\nirrelevant trailer.\n"


def _fixture(step_list_body: str, chip_list_body: str | None = None) -> str:
    """Build a fixture procedure. With `chip_list_body` omitted (the original shape), this is
    byte-identical to what every pre-existing fixture already produced. With it given, a
    '## Chip-sweep step list' H2 is inserted between the P section and the footer -- exercising
    the same _NEXT_H2_RE termination the real two-section PROCEDURE.md relies on.
    """
    text = _FIXTURE_HEADER + "## Step list\n\n" + step_list_body
    if chip_list_body is not None:
        text += "\n## Chip-sweep step list\n\n" + chip_list_body
    return text + _FIXTURE_FOOTER


_POSITIVE_FIXTURE = _fixture(
    "### P-01 — Mount the board\n\nprose.\n\n"
    "### P-02 — Verify port identity\n\nprose.\n\n"
    "### P-03 — Flash and judge\n\nprose.\n"
)

_ARM_CONDITIONAL_FIXTURE = _fixture(
    "### P-01 — Mount the board\n\nprose.\n\n"
    "### P-02 — [arm: control] Verify port identity\n\nprose.\n\n"
    "### P-03 — Flash and judge\n\nprose.\n"
)

_NO_STEP_LIST_FIXTURE = (
    "# Fixture Procedure\n\n## Scope\n\nno step list section anywhere in this file.\n"
)

_EMPTY_STEP_LIST_FIXTURE = (
    "# Fixture Procedure\n\n## Step list\n\nprose with no '### ' headings at all.\n\n"
    "## Outcome taxonomy\n\ntrailer.\n"
)

_DUPLICATE_ID_FIXTURE = _fixture(
    "### P-01 — Mount the board\n\nprose.\n\n"
    "### P-01 — Duplicate of step one\n\nprose.\n"
)

_OUT_OF_ORDER_FIXTURE = _fixture(
    "### P-02 — Second step listed first\n\nprose.\n\n"
    "### P-01 — First step listed second\n\nprose.\n"
)

_UNKNOWN_ARM_FIXTURE = _fixture(
    "### P-01 — Mount the board\n\nprose.\n\n"
    "### P-02 — [arm: bogus] Verify port identity\n\nprose.\n"
)

# --- Amendment 4 (Phase 162): a second, gated section -----------------------------------

_COMBINED_P_BODY = "\n\n".join(
    f"### P-{i:02d} — Fixture WRV step {i}\n\nprose." for i in range(1, 12)
)
_COMBINED_C_BODY = "\n\n".join(
    f"### C-{i:02d} — Fixture chip step {i}\n\nprose." for i in range(1, 10)
)
_COMBINED_FIXTURE = _fixture(_COMBINED_P_BODY, _COMBINED_C_BODY)

_C_HEADING_INSIDE_P_FIXTURE = _fixture(
    "### P-01 — Mount the board\n\nprose.\n\n"
    "### C-01 — Misplaced chip step\n\nprose.\n"
)

_P_HEADING_INSIDE_C_FIXTURE = _fixture(
    "### P-01 — Mount the board\n\nprose.\n",
    "### C-01 — First chip step\n\nprose.\n\n"
    "### P-05 — Misplaced WRV step\n\nprose.\n",
)


def _run_selftest() -> int:
    results: list[tuple[str, bool]] = []

    def report(name: str, ok: bool) -> None:
        results.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'}: {name}")

    tmp = Path(tempfile.mkdtemp(prefix="render_steps_selftest_"))

    # --- positive: an unannotated fixture renders identically for both arms, diff empty ---
    pos_path = tmp / "positive.md"
    pos_path.write_text(_POSITIVE_FIXTURE)
    try:
        control_lines = load_and_render(pos_path, "control")
        v133_lines = load_and_render(pos_path, "v133")
        ok = control_lines == v133_lines and len(control_lines) == 3
    except ProcedureParseError:
        ok = False
    report("positive: unannotated fixture renders identically for both arms (diff empty)", ok)

    # --- negative (the gate's own falsification): one arm-annotated step -> NON-empty diff ---
    cond_path = tmp / "arm_conditional.md"
    cond_path.write_text(_ARM_CONDITIONAL_FIXTURE)
    try:
        control_lines = load_and_render(cond_path, "control")
        v133_lines = load_and_render(cond_path, "v133")
        ok = control_lines != v133_lines and len(control_lines) == 3 and len(v133_lines) == 2
    except ProcedureParseError:
        ok = False
    report(
        "negative: a single [arm: control]-annotated step produces a NON-empty diff "
        "(the gate's own falsification)",
        ok,
    )

    # --- negative: no '## Step list' section at all -> non-zero (ProcedureParseError) ---
    no_list_path = tmp / "no_step_list.md"
    no_list_path.write_text(_NO_STEP_LIST_FIXTURE)
    try:
        load_and_render(no_list_path, "control")
        ok = False
    except ProcedureParseError:
        ok = True
    report("negative: absent '## Step list' section exits non-zero", ok)

    # --- negative: '## Step list' section present but zero '### ' headings -> non-zero ---
    empty_list_path = tmp / "empty_step_list.md"
    empty_list_path.write_text(_EMPTY_STEP_LIST_FIXTURE)
    try:
        load_and_render(empty_list_path, "control")
        ok = False
    except ProcedureParseError:
        ok = True
    report("negative: empty '## Step list' section exits non-zero", ok)

    # --- negative: duplicate step id -> non-zero ---
    dup_path = tmp / "duplicate_id.md"
    dup_path.write_text(_DUPLICATE_ID_FIXTURE)
    try:
        load_and_render(dup_path, "control")
        ok = False
    except ProcedureParseError:
        ok = True
    report("negative: duplicate step id exits non-zero", ok)

    # --- negative: step ids out of ascending order -> non-zero ---
    order_path = tmp / "out_of_order.md"
    order_path.write_text(_OUT_OF_ORDER_FIXTURE)
    try:
        load_and_render(order_path, "control")
        ok = False
    except ProcedureParseError:
        ok = True
    report("negative: step ids out of ascending order exits non-zero", ok)

    # --- negative: annotation naming an unknown arm -> non-zero ---
    unknown_arm_path = tmp / "unknown_arm.md"
    unknown_arm_path.write_text(_UNKNOWN_ARM_FIXTURE)
    try:
        load_and_render(unknown_arm_path, "control")
        ok = False
    except ProcedureParseError:
        ok = True
    report("negative: annotation naming an unknown arm exits non-zero", ok)

    # --- positive (Amendment 4): a fixture with both an 11-step P section and a 9-step C ---
    # --- section renders 11 / 9 lines respectively, each arm-identical ----------------------
    combined_path = tmp / "combined.md"
    combined_path.write_text(_COMBINED_FIXTURE)
    try:
        control_p = load_and_render(combined_path, "control", section="P")
        v133_p = load_and_render(combined_path, "v133", section="P")
        control_c = load_and_render(combined_path, "control", section="C")
        v133_c = load_and_render(combined_path, "v133", section="C")
        ok = (
            control_p == v133_p
            and len(control_p) == 11
            and control_c == v133_c
            and len(control_c) == 9
        )
    except ProcedureParseError:
        ok = False
    report(
        "positive (Amendment 4): a fixture with an 11-step P section and a 9-step C section "
        "renders 9 lines under --section C and 11 under --section P, each arm-identical",
        ok,
    )

    # --- negative (Amendment 4): a C-NN heading inside '## Step list' is refused by name, ---
    # --- and symmetrically a P-NN heading inside the chip section is refused under --section C
    c_in_p_path = tmp / "c_in_p.md"
    c_in_p_path.write_text(_C_HEADING_INSIDE_P_FIXTURE)
    ok_c_in_p = False
    try:
        load_and_render(c_in_p_path, "control", section="P")
    except ProcedureParseError as exc:
        reason = str(exc)
        ok_c_in_p = "C-01" in reason and "P-NN" in reason

    p_in_c_path = tmp / "p_in_c.md"
    p_in_c_path.write_text(_P_HEADING_INSIDE_C_FIXTURE)
    ok_p_in_c = False
    try:
        load_and_render(p_in_c_path, "control", section="C")
    except ProcedureParseError as exc:
        reason = str(exc)
        ok_p_in_c = "P-05" in reason and "C-NN" in reason

    report(
        "negative (Amendment 4): a 'C-NN' heading inside '## Step list' is refused naming the "
        "id and the P-NN pattern, and symmetrically a 'P-NN' heading inside the chip section "
        "is refused under --section C naming the id and the C-NN pattern",
        ok_c_in_p and ok_p_in_c,
    )

    passed = all(ok for _, ok in results)
    print(f"{'PASS' if passed else 'FAIL'}: render_steps.py --selftest ({sum(ok for _, ok in results)}/{len(results)} legs)")
    return 0 if passed else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arm", choices=_ARM_CHOICES, help="which arm's render to emit")
    ap.add_argument(
        "--procedure",
        default=str(_DEFAULT_PROCEDURE),
        help="path to PROCEDURE.md (default: the milestone's own copy)",
    )
    ap.add_argument(
        "--section",
        choices=_SECTION_CHOICES,
        default="P",
        help=(
            "which step-list section to render: 'P' for '## Step list' (the original "
            "behaviour, default) or 'C' for '## Chip-sweep step list' (Amendment 4). "
            "Defaulting to 'P' keeps every pre-existing invocation byte-identical."
        ),
    )
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    if not args.arm:
        print("FAIL: --arm is required (choose one of: control, v133)", file=sys.stderr)
        return 2

    procedure_path = Path(args.procedure)
    if not procedure_path.exists():
        print(f"FAIL: procedure file not found: {procedure_path}", file=sys.stderr)
        return 1

    try:
        lines = load_and_render(procedure_path, args.arm, section=args.section)
    except ProcedureParseError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
