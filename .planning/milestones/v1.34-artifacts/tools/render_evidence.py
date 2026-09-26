#!/usr/bin/env python3
"""render_evidence.py -- renders bench/EVIDENCE.md from bench/EVIDENCE.jsonl (D-15).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo. Pure standard library.

WHAT THIS TOOL DOES
--------------------
`bench/EVIDENCE.jsonl` is the canonical, append-only record (line 1 is a `_schema` header;
every later line is one position's row). `bench/EVIDENCE.md` is a rendered view of that
record and is NEVER hand-edited -- this tool is what makes that a checkable property rather
than an instruction. Three modes:

  (no flag)   Render `--jsonl` to `--target`, overwriting it.
  --check     Re-render `--jsonl` in memory and byte-compare against the committed
              `--target` WITHOUT writing anything. Equal -> exit 0. Different -> exit
              non-zero with a unified diff of the first differing region, so a hand-edit is
              NAMED rather than merely detected. This is the leg with no Python analog in
              this tree (`tools/catalog/codegen.py --check` validates its OWN source and
              exits 0/1; it does not diff a render against a separately committed target).
              The nearest precedent for that comparison is bash (`check-migration.sh`'s
              `cmp -s`), not Python -- so this leg is written deliberately, not adapted.
  --append    Append exactly one new row (from a JSON file, or stdin via `-`) to `--jsonl`.
              Because the record is append-only (D-15), this is implemented as
              read-all -> validate -> reassert the existing prefix is byte-unchanged ->
              write the WHOLE file atomically (temp file + os.replace), never a plain
              `open(..., "a")`, which is not atomic and would leave a torn file on a
              mid-write interruption.

DETERMINISM CONTRACT (mirrors tools/catalog/codegen.py's LCAT-05 contract)
---------------------------------------------------------------------------
Two consecutive renders of the same JSONL produce byte-identical Markdown. Achieved by:
  - rows emitted in a deterministic order derived from the record (sorted by position_id)
  - no timestamp, no hostname, and no value not derived from the JSONL's own schema/rows
  - LF line endings, written explicitly (open(..., newline="\\n"))
  - every hash/numeric/list field formatted identically on every run (json.dumps with a
    fixed separator, no key-sorting inside a row -- record_keys order is preserved)
The prior milestone's evidence Markdown (.planning/milestones/v1.18-artifacts/bench/EVIDENCE.md) carries a
`**Generated:** <ISO-8601 timestamp>` line -- that is the SPECIFIC thing not to copy here,
because a timestamp would make the render non-reproducible and `--check` permanently red.

FAIL CLOSED
-----------
A missing or empty `--jsonl`, a line 1 without the `_schema` header, or a parsed row count
that disagrees with the number of non-header lines in the file, each exit non-zero with a
named `FAIL:` reason. This tool never writes an empty target and exits 0 -- that failure
shape (a gate that discovers/renders nothing and reports success) has already shipped once
in this repo and this tool does not repeat it.

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
_DEFAULT_JSONL = _HERE.parent / "bench" / "EVIDENCE.jsonl"
_DEFAULT_TARGET = _HERE.parent / "bench" / "EVIDENCE.md"


class RenderError(Exception):
    """Fail-closed signal: a named reason, never a silent empty render."""


# ---------------------------------------------------------------------------
# Load + validate the JSONL record
# ---------------------------------------------------------------------------


def load_jsonl(path: Path) -> tuple[dict, list[dict]]:
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
        rows.append(obj)

    if len(rows) != len(lines) - 1:
        # Fail-closed rule: a non-header-only file that somehow parses to zero (or fewer)
        # rows than its own non-header line count is refused rather than silently rendered
        # as an empty table -- the exact "discovered/rendered nothing, exited 0" shape this
        # project has already shipped once.
        raise RenderError(
            f"parsed {len(rows)} row(s) but the file has {len(lines) - 1} non-header "
            "line(s) -- refusing to render a partial table"
        )
    return schema, rows


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


def render_table(record_keys: list[str], rows: list[dict]) -> str:
    header = "| " + " | ".join(record_keys) + " |"
    sep = "| " + " | ".join(["---"] * len(record_keys)) + " |"
    lines = [header, sep]
    for row in rows:
        cells = [_format_cell(row.get(key)) for key in record_keys]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _reconciliation_text(schema: dict, nonbringup_rows: list[dict]) -> str:
    expected = schema.get("position_count_expected", 0)
    validated = sum(1 for r in nonbringup_rows if r.get("outcome") == "validated")
    skipped = sum(1 for r in nonbringup_rows if r.get("outcome") == "skipped-with-reason")
    accounted = validated + skipped
    missing = expected - accounted
    return (
        f"{validated} validated + {skipped} skipped-with-reason = {accounted} of "
        f"{expected} positions accounted for ({missing} not yet recorded)."
    )


def render_markdown(schema: dict, rows: list[dict]) -> str:
    record_keys = schema["record_keys"]
    prefix = schema.get("bringup_cell_id_prefix", "BRINGUP-")

    def _is_bringup(row: dict) -> bool:
        cell_id = row.get("cell_id")
        return isinstance(cell_id, str) and cell_id.startswith(prefix)

    nonbringup_rows = sorted(
        (r for r in rows if not _is_bringup(r)), key=lambda r: str(r.get("position_id", ""))
    )
    bringup_rows = sorted(
        (r for r in rows if _is_bringup(r)), key=lambda r: str(r.get("position_id", ""))
    )

    milestone = schema.get("milestone", "")
    phase_pinned = schema.get("phase_pinned", "")

    lines: list[str] = []
    lines.append(f"# {milestone} Bench Evidence — {phase_pinned}")
    lines.append("")
    lines.append(
        "> This document is generated from `bench/EVIDENCE.jsonl` by "
        "`tools/render_evidence.py` and is never hand-edited. Run "
        "`render_evidence.py --jsonl bench/EVIDENCE.jsonl --target bench/EVIDENCE.md "
        "--check` to verify no drift."
    )
    lines.append("")
    lines.append(
        "Board identity is established by an independent avrdude-signature probe "
        "(`tools/probe_board.py`, PROCEDURE.md P-02), never by a firmware-reported field; "
        "shield revision is operator-declared from the silkscreen (PROCEDURE.md P-01), "
        "because `hw_revision` cannot distinguish this rig's Rev 2.0 / Rev 2.2 / Modified "
        "Rev 0 shields."
    )
    lines.append("")
    lines.append("## Close-out counting rule")
    lines.append("")
    lines.append(schema.get("close01_counting_rule", ""))
    lines.append("")
    lines.append("## Positions (excludes bring-up rows)")
    lines.append("")
    lines.append(render_table(record_keys, nonbringup_rows))
    lines.append("")
    lines.append("## Bring-up rows — rig evidence, excluded from the 20-position count")
    lines.append("")
    lines.append(render_table(record_keys, bringup_rows))
    lines.append("")
    lines.append("## Reconciliation")
    lines.append("")
    lines.append(_reconciliation_text(schema, nonbringup_rows))
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
# --append: read-all, validate, reassert prefix unchanged, atomic replace
# ---------------------------------------------------------------------------


def append_row_to_file(jsonl_path: Path, new_row: dict, _pre_write_hook=None) -> str:
    """Appends new_row to jsonl_path. Returns the appended position_id.

    `_pre_write_hook`, if given, is called with `jsonl_path` after validation but before
    the pre-write re-read -- the injectable seam --selftest uses to simulate a concurrent
    modification of the file's existing rows between this call's initial read and its write,
    without a real race condition or extra process.
    """
    if not jsonl_path.exists():
        raise RenderError(f"--jsonl file does not exist: {jsonl_path}")
    original = jsonl_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    if not lines:
        raise RenderError(f"--jsonl file is empty: {jsonl_path}")

    try:
        header_obj = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise RenderError(f"line 1 is not valid JSON: {exc}") from exc
    schema = header_obj.get("_schema") if isinstance(header_obj, dict) else None
    if not isinstance(schema, dict):
        raise RenderError("line 1 does not carry the '_schema' header record")
    record_keys = schema.get("record_keys")
    if not isinstance(record_keys, list):
        raise RenderError("_schema.record_keys is missing or not a list")
    outcome_domain = schema.get("outcome_domain") or schema.get("outcome_values") or []

    missing = [k for k in record_keys if k not in new_row]
    if missing:
        raise RenderError(f"row omits declared key(s): {missing}")
    extra = [k for k in new_row if k not in record_keys]
    if extra:
        raise RenderError(f"row carries key(s) not declared in record_keys: {extra}")
    if new_row.get("outcome") not in outcome_domain:
        raise RenderError(
            f"row outcome {new_row.get('outcome')!r} is outside the schema's outcome "
            f"domain {outcome_domain!r}"
        )

    existing_position_ids: set = set()
    for lineno, line in enumerate(lines[1:], start=2):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RenderError(f"line {lineno}: not valid JSON: {exc}") from exc
        pid = obj.get("position_id") if isinstance(obj, dict) else None
        if pid is not None:
            existing_position_ids.add(pid)

    new_position_id = new_row.get("position_id")
    if new_position_id in existing_position_ids:
        raise RenderError(
            f"position_id {new_position_id!r} already exists -- a row is never "
            "rewritten once appended"
        )

    if _pre_write_hook is not None:
        _pre_write_hook(jsonl_path)

    current = jsonl_path.read_text(encoding="utf-8")
    if current != original:
        raise RenderError(
            "existing rows changed on disk between read and append -- refusing to write "
            "(append-only integrity: the prefix must be byte-unchanged before replace)"
        )

    ordered_row = {k: new_row[k] for k in record_keys}
    new_content = original
    if not new_content.endswith("\n"):
        new_content += "\n"
    new_content += json.dumps(ordered_row, ensure_ascii=False, separators=(",", ":")) + "\n"
    atomic_write(jsonl_path, new_content)
    return new_position_id


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jsonl", default=str(_DEFAULT_JSONL), help="path to bench/EVIDENCE.jsonl")
    ap.add_argument("--target", default=str(_DEFAULT_TARGET), help="path to bench/EVIDENCE.md")
    ap.add_argument(
        "--check", action="store_true", help="re-render and byte-compare against --target; write nothing"
    )
    ap.add_argument(
        "--append", default=None, help="path to a JSON file holding one row, or '-' for stdin"
    )
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    if args.append is not None:
        jsonl_path = Path(args.jsonl)
        try:
            if args.append == "-":
                raw = sys.stdin.read()
            else:
                raw = Path(args.append).read_text(encoding="utf-8")
            new_row = json.loads(raw)
        except OSError as exc:
            print(f"FAIL: could not read append source: {exc}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as exc:
            print(f"FAIL: append source is not valid JSON: {exc}", file=sys.stderr)
            return 1
        if not isinstance(new_row, dict):
            print("FAIL: append source is not a JSON object", file=sys.stderr)
            return 1
        try:
            appended_id = append_row_to_file(jsonl_path, new_row)
        except RenderError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        print(f"OK: appended position_id={appended_id!r} to {jsonl_path}")
        return 0

    try:
        schema, rows = load_jsonl(Path(args.jsonl))
    except RenderError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    rendered = render_markdown(schema, rows)

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
        print("FAIL: committed target diverges from a fresh render -- hand-edit suspected", file=sys.stderr)
        print(diff, file=sys.stderr)
        return 1

    atomic_write(Path(args.target), rendered)
    print(f"OK: rendered {args.jsonl} -> {args.target}")
    return 0


# ---------------------------------------------------------------------------
# --selftest: on-disk fixtures in a temp directory. Positive legs + 7 named
# negative legs, per the gate_record.py idiom (accumulate, never bail on the
# first failure).
# ---------------------------------------------------------------------------


def _run_selftest() -> int:
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
        "record_keys": ["position_id", "cell_id", "outcome", "note"],
        "outcome_domain": ["validated", "skipped-with-reason"],
        "outcome_values": ["validated", "skipped-with-reason"],
        "milestone": "vX.Y-selftest",
        "phase_pinned": "selftest-fixture-phase",
        "bringup_cell_id_prefix": "BRINGUP-",
        "position_count_expected": 2,
        "close01_counting_rule": "selftest fixture counting rule",
    }

    def header_line() -> str:
        return json.dumps({"_schema": good_schema}, ensure_ascii=False, separators=(",", ":"))

    def row_line(**overrides) -> str:
        row = {
            "position_id": "A1__control__w27c512",
            "cell_id": "A1",
            "outcome": "validated",
            "note": "not measured — fixture only, no board attached",
        }
        row.update(overrides)
        return json.dumps(row, ensure_ascii=False, separators=(",", ":"))

    tmp = Path(tempfile.mkdtemp(prefix="render_evidence_selftest_"))
    try:
        # --- positive: two-row fixture renders identically on two runs ---
        jsonl_path = tmp / "good.jsonl"
        jsonl_path.write_text(
            header_line() + "\n" + row_line() + "\n"
            + row_line(position_id="A2__control__w27c512", cell_id="A2") + "\n",
            encoding="utf-8",
        )
        target_a = tmp / "a.md"
        target_b = tmp / "b.md"
        try:
            schema, rows = load_jsonl(jsonl_path)
            rendered_a = render_markdown(schema, rows)
            rendered_b = render_markdown(schema, rows)
            report("positive: rendering twice is byte-identical", rendered_a == rendered_b)
        except RenderError as exc:
            report("positive: rendering twice is byte-identical", False, str(exc))
            rendered_a = ""

        atomic_write(target_a, rendered_a)
        atomic_write(target_b, rendered_a)

        # --- positive: --check against a freshly rendered target is green ---
        try:
            schema2, rows2 = load_jsonl(jsonl_path)
            fresh = render_markdown(schema2, rows2)
            report("positive: --check against a freshly rendered target is green", fresh == target_a.read_text(encoding="utf-8"))
        except RenderError as exc:
            report("positive: --check against a freshly rendered target is green", False, str(exc))

        # --- positive: appending a valid row preserves earlier rows byte-for-byte ---
        append_src = tmp / "good.jsonl"
        before = append_src.read_text(encoding="utf-8")
        new_row = {
            "position_id": "B1__control__w27c512",
            "cell_id": "B1",
            "outcome": "skipped-with-reason",
            "note": "not measured — fixture leg, write skipped",
        }
        try:
            append_row_to_file(append_src, new_row)
            after = append_src.read_text(encoding="utf-8")
            report(
                "positive: append preserves earlier rows byte-for-byte",
                after.startswith(before) and after != before,
            )
        except RenderError as exc:
            report("positive: append preserves earlier rows byte-for-byte", False, str(exc))

        # --- negative 1: a one-character edit to the target fails --check, diff names the line ---
        edited = tmp / "edited.md"
        edited.write_text(target_a.read_text(encoding="utf-8") + "x\n", encoding="utf-8")
        try:
            schema3, rows3 = load_jsonl(jsonl_path)
            fresh3 = render_markdown(schema3, rows3)
            committed3 = edited.read_text(encoding="utf-8")
            diff_nonempty = committed3 != fresh3
            diff_text = "\n".join(
                difflib.unified_diff(committed3.splitlines(), fresh3.splitlines(), lineterm="")
            )
            report(
                "negative 1: one-character-edited target fails --check with a named diff",
                diff_nonempty and bool(diff_text),
            )
        except RenderError as exc:
            report("negative 1: one-character-edited target fails --check with a named diff", False, str(exc))

        # --- negative 2: fixture whose line 1 lacks the header ---
        no_header = tmp / "no_header.jsonl"
        no_header.write_text(row_line() + "\n", encoding="utf-8")
        try:
            load_jsonl(no_header)
            report("negative 2: jsonl missing the line-1 header is caught", False, "did not raise")
        except RenderError as exc:
            report("negative 2: jsonl missing the line-1 header is caught", True, str(exc))

        # --- negative 3: empty jsonl ---
        empty_jsonl = tmp / "empty.jsonl"
        empty_jsonl.write_text("", encoding="utf-8")
        try:
            load_jsonl(empty_jsonl)
            report("negative 3: empty jsonl is caught", False, "did not raise")
        except RenderError as exc:
            report("negative 3: empty jsonl is caught", True, str(exc))

        # --- negative 4: append whose row omits a declared key ---
        omits_key_src = tmp / "omits_key.jsonl"
        omits_key_src.write_text(header_line() + "\n" + row_line() + "\n", encoding="utf-8")
        try:
            append_row_to_file(omits_key_src, {"position_id": "C1__control__w27c512", "cell_id": "C1", "outcome": "validated"})
            report("negative 4: append omitting a declared key is caught", False, "did not raise")
        except RenderError as exc:
            report("negative 4: append omitting a declared key is caught", True, str(exc))

        # --- negative 5: append whose outcome is outside the domain ---
        bad_outcome_src = tmp / "bad_outcome.jsonl"
        bad_outcome_src.write_text(header_line() + "\n" + row_line() + "\n", encoding="utf-8")
        try:
            append_row_to_file(
                bad_outcome_src,
                {"position_id": "C2__control__w27c512", "cell_id": "C2", "outcome": "inconclusive", "note": "x"},
            )
            report("negative 5: append with an out-of-domain outcome is caught", False, "did not raise")
        except RenderError as exc:
            report("negative 5: append with an out-of-domain outcome is caught", True, str(exc))

        # --- negative 6: append whose position_id already exists ---
        dup_src = tmp / "dup.jsonl"
        dup_src.write_text(header_line() + "\n" + row_line() + "\n", encoding="utf-8")
        try:
            append_row_to_file(
                dup_src,
                {"position_id": "A1__control__w27c512", "cell_id": "A1", "outcome": "validated", "note": "x"},
            )
            report("negative 6: append with a duplicate position_id is caught", False, "did not raise")
        except RenderError as exc:
            report("negative 6: append with a duplicate position_id is caught", True, str(exc))

        # --- negative 7: append against a file whose earlier rows were altered mid-operation ---
        altered_src = tmp / "altered.jsonl"
        altered_src.write_text(header_line() + "\n" + row_line() + "\n", encoding="utf-8")

        def _mutate(path: Path) -> None:
            path.write_text(path.read_text(encoding="utf-8") + row_line(position_id="ZZ__control__w27c512", cell_id="ZZ") + "\n", encoding="utf-8")

        try:
            append_row_to_file(
                altered_src,
                {"position_id": "D1__control__w27c512", "cell_id": "D1", "outcome": "validated", "note": "x"},
                _pre_write_hook=_mutate,
            )
            report("negative 7: append against a mid-operation-altered prefix is caught", False, "did not raise")
        except RenderError as exc:
            report("negative 7: append against a mid-operation-altered prefix is caught", True, str(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_pass = "ok" if ok_overall else "FAILED"
    print(f"render_evidence.py --selftest overall: {n_pass}")
    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
