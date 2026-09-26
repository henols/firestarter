#!/usr/bin/env python3
"""render_chip_evidence.py -- renders bench/CHIP-EVIDENCE.md from bench/CHIP-EVIDENCE.jsonl.

Sibling to tools/render_evidence.py (the WRV renderer): same determinism contract, same
`--check` byte-compare shape, different document body -- this file's own arithmetic (SC#4's
`10 + N` reconciliation) and its own row partition (arm == primary_arm vs. a control
re-run), not the WRV record's bring-up-prefix exclusion.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo. Pure standard library.

WHAT THIS TOOL DOES
--------------------
`bench/CHIP-EVIDENCE.jsonl` is the chip sweep's canonical, append-only record (line 1 is a
`_schema` header; every later line is one position's row -- either a v133 sweep position or
a divergence-arbitration control re-run). `bench/CHIP-EVIDENCE.md` is a rendered view of
that record and is NEVER hand-edited -- this tool is what makes that a checkable property
rather than an instruction. Two modes:

  (no flag)   Render `--jsonl` to `--target`, overwriting it.
  --check     Re-render `--jsonl` in memory and byte-compare against the committed
              `--target` WITHOUT writing anything. Equal -> exit 0. Different -> exit
              non-zero with a unified diff of the first differing region printed to
              stderr, so a hand-edit is NAMED rather than merely detected.

Appending a row is NOT this tool's job -- tools/append_chip_evidence.py owns deriving and
appending a row, and delegates the actual atomic-append mechanics to
tools/render_evidence.py's `append_row_to_file` (this file's own sibling), never
re-implementing them here.

DETERMINISM CONTRACT (mirrors render_evidence.py's, itself mirroring codegen.py's LCAT-05)
---------------------------------------------------------------------------------------------
Two consecutive renders of the same JSONL produce byte-identical Markdown. Achieved by:
  - rows emitted in a deterministic order derived from the record (sorted by position_id)
  - no timestamp, no hostname, and no value not derived from the JSONL's own schema/rows
  - LF line endings, written explicitly (open(..., newline="\\n"))
  - every hash/numeric/list/dict field formatted identically on every run (json.dumps with
    a fixed separator and sort_keys=True, independent of the row's own key order)
The prior milestone's evidence Markdown (.planning/milestones/v1.18-artifacts/bench/EVIDENCE.md) carries a
`**Generated:** <ISO-8601 timestamp>` line -- that is the SPECIFIC thing not to copy here,
because a timestamp would make the render non-reproducible and `--check` permanently red.

ROW PARTITION -- SCHEMA-DRIVEN, NO LITERAL FALLBACK
-----------------------------------------------------
Unlike render_evidence.py's rig-evidence exclusion prefix (a schema-driven value that falls
back to a hardcoded literal when the schema omits it), this file's row partition never
falls back to a literal: `_schema.primary_arm` and `_schema.record_keys` carrying a
`named_absence` column are both REQUIRED, and their absence is a named refusal, not a
guess. A hidden default here could silently mis-count a control re-run or the one
named-absence position (the 2516, never seated) -- this is the one thing the WRV analog's
own idiom must NOT be copied for.

FAIL CLOSED
-----------
A missing or empty `--jsonl`, a line 1 without the `_schema` header, a `_schema` without a
`record_keys` list, a row carrying a key outside `record_keys`, a parsed row count that
disagrees with the file's non-header line count, or a schema missing either row-partition
discriminator, each exit non-zero with a named `FAIL:` reason. This tool never writes an
empty target and exits 0.

Entry point is `sys.exit(main())`, per rig-pins.json's tool_conventions.entry_point_idiom.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_JSONL = _HERE.parent / "bench" / "CHIP-EVIDENCE.jsonl"
_DEFAULT_TARGET = _HERE.parent / "bench" / "CHIP-EVIDENCE.md"

_DIVERGING_PREFIX = "diverges"
_DIVERGENCE_TABLE_COLUMNS = [
    "chip",
    "prior_disposition_source",
    "prior_disposition",
    "step_verdicts",
    "divergence_verdict",
    "known_carried",
]


class RenderError(Exception):
    """Fail-closed signal: a named reason, never a silent empty render."""


# ---------------------------------------------------------------------------
# Load + validate the JSONL record
# ---------------------------------------------------------------------------


def load_schema_and_rows(path: Path) -> tuple[dict, list[dict]]:
    if not path.exists():
        raise RenderError(f"--jsonl file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise RenderError(f"--jsonl file is empty: {path}")

    lines = text.splitlines()
    try:
        header_obj = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise RenderError(f"line 1 is not valid JSON: {exc}") from exc
    if not isinstance(header_obj, dict) or "_schema" not in header_obj:
        raise RenderError("line 1 does not carry the '_schema' header record")
    schema = header_obj["_schema"]
    if not isinstance(schema, dict) or not isinstance(schema.get("record_keys"), list):
        raise RenderError("_schema.record_keys is missing or not a list")
    record_keys = schema["record_keys"]

    rows: list[dict] = []
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            raise RenderError(f"line {lineno}: blank line in a JSONL file")
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RenderError(f"line {lineno}: not valid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise RenderError(f"line {lineno}: not a JSON object")
        if "_schema" in obj:
            raise RenderError(f"line {lineno}: '_schema' key must appear only on line 1")
        extra = [k for k in obj if k not in record_keys]
        if extra:
            raise RenderError(
                f"line {lineno}: row carries key(s) not declared in record_keys: {extra}"
            )
        rows.append(obj)

    if len(rows) != len(lines) - 1:
        raise RenderError(
            f"parsed {len(rows)} row(s) but the file has {len(lines) - 1} non-header "
            "line(s) -- refusing to render a partial table"
        )
    return schema, rows


# ---------------------------------------------------------------------------
# Row partition -- schema-driven, no literal fallback
# ---------------------------------------------------------------------------


def _partition_rows(schema: dict, rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Splits rows into (primary sweep positions, divergence-arbitration control re-runs).

    Driven entirely from the schema: `primary_arm` names the sweep arm; any row whose `arm`
    differs from it is a control re-run under `control_rerun_exclusion`'s semantics. Both
    discriminators required here -- `primary_arm` and the `named_absence` record-key -- are
    hard requirements with no literal fallback: a schema missing either is refused by name.
    """
    if "primary_arm" not in schema:
        raise RenderError(
            "_schema has no 'primary_arm' -- refusing to guess the sweep/control-re-run "
            "discriminator"
        )
    record_keys = schema["record_keys"]
    if "named_absence" not in record_keys:
        raise RenderError(
            "_schema's record_keys carries no 'named_absence' column -- refusing to guess "
            "how a named absence is identified"
        )
    primary_arm = schema["primary_arm"]
    primary_rows = sorted(
        (r for r in rows if r.get("arm") == primary_arm),
        key=lambda r: str(r.get("position_id", "")),
    )
    control_rows = sorted(
        (r for r in rows if r.get("arm") != primary_arm),
        key=lambda r: str(r.get("position_id", "")),
    )
    return primary_rows, control_rows


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _format_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    elif isinstance(value, bool):
        text = "true" if value else "false"
    else:
        text = str(value)
    # Markdown table cell escaping: pipes and embedded newlines would break the row.
    return text.replace("|", "\\|").replace("\n", " ")


def render_table(columns: list[str], rows: list[dict]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for row in rows:
        cells = [_format_cell(row.get(key)) for key in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _divergence_table(primary_rows: list[dict]) -> str:
    """SC#3's table: one row per primary position, every cell present, none blank.

    A not-measured-with-reason string is a value; a blank (None or "") is not, and is a
    named refusal here rather than a silently empty cell.
    """
    for row in primary_rows:
        for col in _DIVERGENCE_TABLE_COLUMNS:
            value = row.get(col)
            if value is None or value == "":
                raise RenderError(
                    f"position_id={row.get('position_id')!r}: divergence-table column "
                    f"{col!r} is blank -- a not-measured-with-reason string is a value, a "
                    "blank is not"
                )
    return render_table(_DIVERGENCE_TABLE_COLUMNS, primary_rows)


def _reconciliation_text(schema: dict, primary_rows: list[dict]) -> str:
    """The close-out statement (SC#1/CLOSE-01): validated + skipped == position_count_expected."""
    expected = schema.get("position_count_expected", 0)
    validated = sum(1 for r in primary_rows if r.get("outcome") == "validated")
    skipped = sum(1 for r in primary_rows if r.get("outcome") == "skipped-with-reason")
    accounted = validated + skipped
    missing = expected - accounted
    return (
        f"{validated} validated + {skipped} skipped-with-reason = {accounted} of "
        f"{expected} positions accounted for ({missing} not yet recorded)."
    )


def _sc04_text(schema: dict, primary_rows: list[dict], control_rows: list[dict]) -> str:
    """The SC#4 statement: three conjoined identities plus the 10 + N / 11 + N reading.

    Evaluated as an equation over rows, never as a human count. The 2516 named absence is
    never run, so it never carries a `divergence_verdict` starting with `_DIVERGING_PREFIX`
    -- it therefore naturally never contributes to the diverging-count term below, holding
    even at N == 0 (before a single control re-run has ever been recorded).
    """
    n_control = len(control_rows)
    diverging_primary = [
        r
        for r in primary_rows
        if isinstance(r.get("divergence_verdict"), str)
        and r["divergence_verdict"].startswith(_DIVERGING_PREFIX)
    ]
    n_diverging = len(diverging_primary)
    diverging_ids = {r.get("position_id") for r in diverging_primary}
    control_for = [r.get("control_rerun_for") for r in control_rows]
    all_named_existing = all(cf in diverging_ids for cf in control_for)
    no_duplicates = len(control_for) == len(set(control_for))
    counts_match = n_control == n_diverging
    total_runs = 10 + n_control
    roadmap_runs = 11 + n_control
    primary_arm = schema.get("primary_arm", "")

    return (
        f"SC#4: count(control)={n_control} == count({primary_arm} rows whose "
        f"divergence_verdict starts {_DIVERGING_PREFIX!r})={n_diverging}: "
        f"{'holds' if counts_match else 'FAILS'}. Every control row's control_rerun_for "
        f"names an existing diverging {primary_arm} row: "
        f"{'yes' if all_named_existing else 'NO'}. No two control rows share the same "
        f"control_rerun_for: {'yes' if no_duplicates else 'NO'}. Total runs this cell "
        f"records: 10 + N = 10 + {n_control} = {total_runs} (the roadmap's reading is "
        f"11 + N = 11 + {n_control} = {roadmap_runs}; this file deliberately uses 10, not "
        "11, as the run-count base, because the 2516 is a named absence -- never seated, "
        "never run -- and contributes 0 to this term)."
    )


def render_markdown(schema: dict, rows: list[dict]) -> str:
    record_keys = schema["record_keys"]
    primary_rows, control_rows = _partition_rows(schema, rows)
    primary_arm = schema["primary_arm"]

    milestone = schema.get("milestone", "")
    phase_pinned = schema.get("phase_pinned", "")

    lines: list[str] = []
    lines.append(f"# {milestone} Chip Sweep Evidence — {phase_pinned}")
    lines.append("")
    lines.append(
        "> This document is generated from `bench/CHIP-EVIDENCE.jsonl` by "
        "`tools/render_chip_evidence.py` and is never hand-edited. Run "
        "`render_chip_evidence.py --jsonl bench/CHIP-EVIDENCE.jsonl --target "
        "bench/CHIP-EVIDENCE.md --check` to verify no drift."
    )
    lines.append("")
    lines.append(
        "Each row is produced by `firestarter dev test <chip>` on Leonardo + Rev 2.0, "
        "v1.33 firmware, and copied out of the frozen config dir by "
        "`tools/append_chip_evidence.py` -- never hand-entered."
    )
    lines.append("")
    lines.append("## Close-out counting rule")
    lines.append("")
    lines.append(schema.get("close01_counting_rule", ""))
    lines.append("")
    lines.append(f"## Positions (arm == {primary_arm!r})")
    lines.append("")
    lines.append(render_table(record_keys, primary_rows))
    lines.append("")
    lines.append("## Excluded rows — divergence-arbitration control re-runs")
    lines.append("")
    lines.append(schema.get("control_rerun_exclusion", ""))
    lines.append("")
    lines.append(render_table(record_keys, control_rows))
    lines.append("")
    lines.append("## Divergence table")
    lines.append("")
    lines.append(_divergence_table(primary_rows))
    lines.append("")
    lines.append("## Reconciliation")
    lines.append("")
    lines.append(_reconciliation_text(schema, primary_rows))
    lines.append("")
    lines.append(_sc04_text(schema, primary_rows, control_rows))
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    os.replace(tmp_path, path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--jsonl", default=str(_DEFAULT_JSONL), help="path to bench/CHIP-EVIDENCE.jsonl"
    )
    ap.add_argument(
        "--target", default=str(_DEFAULT_TARGET), help="path to bench/CHIP-EVIDENCE.md"
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="re-render and byte-compare against --target; write nothing",
    )
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    try:
        schema, rows = load_schema_and_rows(Path(args.jsonl))
        rendered = render_markdown(schema, rows)
    except RenderError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.check:
        target_path = Path(args.target)
        if not target_path.exists():
            print(f"FAIL: --check target does not exist: {target_path}", file=sys.stderr)
            return 1
        committed = target_path.read_text(encoding="utf-8")
        if committed == rendered:
            print(f"OK: {target_path} matches a fresh render of {args.jsonl} (--check green)")
            return 0
        diff = "\n".join(
            difflib.unified_diff(
                committed.splitlines(),
                rendered.splitlines(),
                fromfile=str(target_path),
                tofile="<fresh render>",
                lineterm="",
            )
        )
        print(
            "FAIL: committed target diverges from a fresh render -- hand-edit suspected",
            file=sys.stderr,
        )
        print(diff, file=sys.stderr)
        return 1

    atomic_write(Path(args.target), rendered)
    print(f"OK: rendered {args.jsonl} -> {args.target}")
    return 0


# ---------------------------------------------------------------------------
# --selftest: on-disk fixtures in a temp directory. 5 positive legs + 4 named
# negative legs, accumulate-then-report, per the render_evidence.py idiom.
# ---------------------------------------------------------------------------


def _run_selftest() -> int:  # noqa: C901 -- accumulate-then-report selftest, not control flow
    import contextlib
    import io
    import shutil
    import tempfile

    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    good_schema = {
        "record_keys": [
            "chip",
            "position_id",
            "arm",
            "outcome",
            "divergence_verdict",
            "control_rerun_for",
            "prior_disposition_source",
            "prior_disposition",
            "step_verdicts",
            "known_carried",
            "named_absence",
        ],
        "outcome_domain": ["validated", "skipped-with-reason"],
        "outcome_values": ["validated", "skipped-with-reason"],
        "milestone": "vX.Y-selftest",
        "phase_pinned": "selftest-fixture-phase",
        "position_count_expected": 3,
        "primary_arm": "v133",
        "close01_counting_rule": "selftest fixture counting rule",
        "chip_sc04_rule": "selftest fixture sc04 rule",
        "control_rerun_exclusion": "selftest fixture control-rerun exclusion text",
    }

    row_a = {
        "chip": "w27c512",
        "position_id": "POS-A",
        "arm": "v133",
        "outcome": "validated",
        "divergence_verdict": "same",
        "control_rerun_for": None,
        "prior_disposition_source": "v1.15 P83",
        "prior_disposition": "validated",
        "step_verdicts": {"id": "OK"},
        "known_carried": False,
        "named_absence": None,
    }
    row_b = {
        "chip": "w27e512",
        "position_id": "POS-B",
        "arm": "v133",
        "outcome": "validated",
        "divergence_verdict": "diverges — stuck erase bit @0x3d",
        "control_rerun_for": None,
        "prior_disposition_source": "v1.15 P83",
        "prior_disposition": "validated",
        "step_verdicts": {"id": "OK", "write": "BAD"},
        "known_carried": True,
        "named_absence": None,
    }
    row_b_control = {
        "chip": "w27e512",
        "position_id": "POS-B__control",
        "arm": "control",
        "outcome": "validated",
        "divergence_verdict": None,
        "control_rerun_for": "POS-B",
        "prior_disposition_source": None,
        "prior_disposition": None,
        "step_verdicts": None,
        "known_carried": None,
        "named_absence": None,
    }
    row_c_named_absence = {
        "chip": "2516",
        "position_id": "POS-C",
        "arm": "v133",
        "outcome": "skipped-with-reason",
        "divergence_verdict": "not measured — named absence, never seated",
        "control_rerun_for": None,
        "prior_disposition_source": "not measured — never seated",
        "prior_disposition": "not measured — never seated",
        "step_verdicts": {},
        "known_carried": False,
        "named_absence": True,
    }

    def header_line(schema: dict) -> str:
        return json.dumps({"_schema": schema}, ensure_ascii=False, separators=(",", ":"))

    def jsonl_text(schema: dict, rows: list[dict]) -> str:
        text = header_line(schema) + "\n"
        for r in rows:
            text += json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n"
        return text

    tmp = Path(tempfile.mkdtemp(prefix="render_chip_evidence_selftest_"))
    try:
        fixture_rows = [row_a, row_b, row_b_control, row_c_named_absence]
        good_path = tmp / "good.jsonl"
        good_path.write_text(jsonl_text(good_schema, fixture_rows), encoding="utf-8")

        # --- positive 1: two renders of the same input are byte-identical ---
        rendered_a = ""
        try:
            schema1, rows1 = load_schema_and_rows(good_path)
            rendered_a = render_markdown(schema1, rows1)
            rendered_b = render_markdown(schema1, rows1)
            report("positive 1: rendering twice is byte-identical", rendered_a == rendered_b)
        except RenderError as exc:
            report("positive 1: rendering twice is byte-identical", False, str(exc))

        target_a = tmp / "good.md"
        atomic_write(target_a, rendered_a)

        # --- positive 2: --check is green against a freshly rendered target ---
        try:
            schema2, rows2 = load_schema_and_rows(good_path)
            fresh = render_markdown(schema2, rows2)
            report(
                "positive 2: --check is green against a freshly rendered target",
                fresh == target_a.read_text(encoding="utf-8"),
            )
        except RenderError as exc:
            report("positive 2: --check is green against a freshly rendered target", False, str(exc))

        # --- positive 3: --check is red on a byte-mutated target, unified diff, writes nothing ---
        mutated = tmp / "mutated.md"
        mutated.write_text(target_a.read_text(encoding="utf-8") + "x\n", encoding="utf-8")
        before_mutated = mutated.read_text(encoding="utf-8")
        try:
            schema3, rows3 = load_schema_and_rows(good_path)
            fresh3 = render_markdown(schema3, rows3)
            committed3 = mutated.read_text(encoding="utf-8")
            diff_text = "\n".join(
                difflib.unified_diff(committed3.splitlines(), fresh3.splitlines(), lineterm="")
            )
            after_mutated = mutated.read_text(encoding="utf-8")
            report(
                "positive 3: --check is red on a byte-mutated target with a named diff, writes nothing",
                committed3 != fresh3 and bool(diff_text) and after_mutated == before_mutated,
            )
        except RenderError as exc:
            report(
                "positive 3: --check is red on a byte-mutated target with a named diff, writes nothing",
                False,
                str(exc),
            )

        # --- positive 4: reconciliation states 10 + N with the 11 + N deviation, same line ---
        try:
            schema4, rows4 = load_schema_and_rows(good_path)
            rendered4 = render_markdown(schema4, rows4)
            n_control = sum(1 for r in rows4 if r.get("arm") == "control")
            expect_a = f"10 + {n_control} = {10 + n_control}"
            expect_b = f"11 + {n_control} = {11 + n_control}"
            same_line = any(
                expect_a in line and expect_b in line for line in rendered4.splitlines()
            )
            report(
                "positive 4: reconciliation states 10 + N with the 11 + N deviation on the same line",
                same_line,
            )
        except RenderError as exc:
            report(
                "positive 4: reconciliation states 10 + N with the 11 + N deviation on the same line",
                False,
                str(exc),
            )

        # --- positive 5: a named-absence row counts in close-out, excluded from SC#4 ---
        try:
            schema5, rows5 = load_schema_and_rows(good_path)
            primary5, _control5 = _partition_rows(schema5, rows5)
            reconciliation5 = _reconciliation_text(schema5, primary5)
            diverging_primary5 = [
                r
                for r in primary5
                if isinstance(r.get("divergence_verdict"), str)
                and r["divergence_verdict"].startswith(_DIVERGING_PREFIX)
            ]
            named_absence_row = next(r for r in primary5 if r.get("named_absence"))
            counted_in_closeout = reconciliation5 == (
                "2 validated + 1 skipped-with-reason = 3 of 3 positions accounted for "
                "(0 not yet recorded)."
            )
            excluded_from_sc04 = (
                len(diverging_primary5) == 1
                and named_absence_row["position_id"]
                not in {r["position_id"] for r in diverging_primary5}
            )
            report(
                "positive 5: a named-absence row counts in close-out but is excluded from SC#4",
                counted_in_closeout and excluded_from_sc04,
            )
        except RenderError as exc:
            report(
                "positive 5: a named-absence row counts in close-out but is excluded from SC#4",
                False,
                str(exc),
            )

        # --- negative 1: a row key outside record_keys is refused by name ---
        extra_key_path = tmp / "extra_key.jsonl"
        bad_row = dict(row_a)
        bad_row["bogus_field"] = "nope"
        extra_key_path.write_text(jsonl_text(good_schema, [bad_row]), encoding="utf-8")
        try:
            load_schema_and_rows(extra_key_path)
            report("negative 1: a row key outside record_keys is refused by name", False, "did not raise")
        except RenderError as exc:
            report(
                "negative 1: a row key outside record_keys is refused by name",
                "bogus_field" in str(exc),
                str(exc),
            )

        # --- negative 2: line 1 without a _schema header is refused by name ---
        no_schema_path = tmp / "no_schema.jsonl"
        no_schema_path.write_text(
            json.dumps(row_a, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
        )
        try:
            load_schema_and_rows(no_schema_path)
            report("negative 2: line 1 without a _schema header is refused by name", False, "did not raise")
        except RenderError as exc:
            report("negative 2: line 1 without a _schema header is refused by name", True, str(exc))

        # --- negative 3: --check against a missing target is refused by name, exit 1 ---
        old_argv = sys.argv
        try:
            sys.argv = [
                "render_chip_evidence.py",
                "--jsonl",
                str(good_path),
                "--target",
                str(tmp / "does_not_exist.md"),
                "--check",
            ]
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = main()
            report(
                "negative 3: --check against a missing target is refused by name, exit 1",
                rc == 1 and "does not exist" in err.getvalue(),
                err.getvalue().strip(),
            )
        finally:
            sys.argv = old_argv

        # --- negative 4: a schema missing BOTH partition discriminators is refused, never defaulted ---
        missing_discriminators_schema = dict(good_schema)
        missing_discriminators_schema.pop("primary_arm", None)
        missing_discriminators_schema["record_keys"] = [
            k for k in good_schema["record_keys"] if k != "named_absence"
        ]
        stripped_row_a = {k: v for k, v in row_a.items() if k != "named_absence"}
        no_discriminator_path = tmp / "no_discriminator.jsonl"
        no_discriminator_path.write_text(
            jsonl_text(missing_discriminators_schema, [stripped_row_a]), encoding="utf-8"
        )
        try:
            schema6, rows6 = load_schema_and_rows(no_discriminator_path)
            _partition_rows(schema6, rows6)
            report(
                "negative 4: a schema missing both the control-re-run and named-absence "
                "discriminators is refused, never defaulted",
                False,
                "did not raise",
            )
        except RenderError as exc:
            report(
                "negative 4: a schema missing both the control-re-run and named-absence "
                "discriminators is refused, never defaulted",
                True,
                str(exc),
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = "ok" if ok_overall else "FAILED"
    print(f"render_chip_evidence.py --selftest overall: {n_pass}")
    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
