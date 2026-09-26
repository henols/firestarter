#!/usr/bin/env python3
"""gate_record.py -- validates a cell record's completeness, command lines, and outcome
domain (D-17 script half, D-18).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.

Two modes:
  --cell PATH   validates ONE record file. The file's top-level JSON object must carry a
                "_schema" key (record_keys + outcome_values, the same shape as an
                EVIDENCE.jsonl header) alongside its own data fields.
  --jsonl PATH  validates a whole EVIDENCE.jsonl: line 1 must carry the "_schema" header
                record and NO other line may; every later line is a JSON object validated
                against that header's declared record_keys / outcome_values.

Both modes read the required-field list and the permitted outcome domain from the file
under examination, never from a constant baked into this tool -- so this gate's own
correctness does not depend on staying in sync with whatever schema a later plan settles
on. Violations are ACCUMULATED across every check, never returned on the first failure, so
a single run against a 20-row file names every gap in one pass (the v1.33
build_citation_manifest.py self_check() idiom).

Field presence and non-nullity treats "missing" and "still a placeholder" as the SAME
failure (the v1.18 check_graduation.py idiom) -- with one permitted exception, this
project's anti-fabrication convention: a value of the exact shape
"not measured <separator> <reason>" (separator is an em dash or a double hyphen) is
accepted, because the blocking reason travels with the non-claim on the same line. A bare
"not measured" with no reason, or any other blank/placeholder value, is rejected.

Command-line re-parse rejects any `commands` entry whose first token is not an absolute
path equal to one of the two pinned arm binaries, the pinned avrdude binary, the pinned
PlatformIO binary, or the system interpreter invoking a script under
.planning/milestones/v1.34-artifacts/tools/. A bare `firestarter` on PATH resolves to a THIRD, un-named arm (the
user-site editable install) -- this is precisely what this check exists to catch. Any
command carrying a flag from rig-pins.json's forbidden_flags is rejected by name (Phase
145 D-17's withdrawn --force permission, enforced mechanically). Any `pio` invocation whose
recorded cwd is not the pinned PlatformIO project directory is rejected, because the same
command string succeeds or fails depending on cwd (Pitfall 4).

Outcome domain holds every `outcome` value to the two-state set declared in the schema
under examination (D-18): anything that is not a clean pass is a fail, anything not
attempted is a skip. A third state belongs only to Phase 165's triage classification of a
failure after the fact, never to a cell result.

Cross-oracle consistency flags a disagreement between a validated outcome and a mismatched
written/read SHA pair, and a disagreement between the judged SHA verdict and any recorded
unjudged app verdict, as a FINDING (non-zero exit) rather than silently resolving it.

Config-dir integrity recomputes the shared config dir's content SHA (via
tools/check_arms.py's canonical compute_config_dir_sha(), never re-derived here) and
compares it against any `config_dir_sha` a record carries, so a write by either arm becomes
a visible, recorded event (D-07) rather than invisible drift.

No SHA is ever hardcoded in this gate -- every hash is read from the record under
examination, or recomputed live from the filesystem.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_PINS = _HERE.parent / "rig-pins.json"

_NOT_MEASURED_RE = re.compile(r"^not measured\s*(?:—|--)\s*\S.*$", re.IGNORECASE)
_PLACEHOLDER_VALUES = {"TBD", "PENDING", "PLACEHOLDER", "TODO", "PENDING-XSHOWVECTOR"}


# ---------------------------------------------------------------------------
# check_arms.py reuse -- compute_config_dir_sha only. No SHA algorithm is
# re-derived here.
# ---------------------------------------------------------------------------


def _load_check_arms():
    spec = importlib.util.spec_from_file_location("check_arms", _HERE / "check_arms.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Field presence / non-nullity / placeholder / "not measured — reason" idiom
# ---------------------------------------------------------------------------


def _is_acceptable_not_measured(value: object) -> bool:
    return isinstance(value, str) and bool(_NOT_MEASURED_RE.match(value.strip()))


def _is_blank_or_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return True
        if stripped.upper() in _PLACEHOLDER_VALUES:
            return True
        if stripped.lower().startswith("not measured") and not _is_acceptable_not_measured(value):
            return True
    return False


def check_required_fields(record: dict, required_keys: list) -> list[str]:
    violations: list[str] = []
    for key in required_keys:
        if key not in record:
            violations.append(f"required field {key!r} is missing")
            continue
        value = record[key]
        if _is_acceptable_not_measured(value):
            continue
        if _is_blank_or_placeholder(value):
            violations.append(f"required field {key!r} is null/blank/placeholder: {value!r}")
    return violations


# ---------------------------------------------------------------------------
# Command-line re-parse
# ---------------------------------------------------------------------------


def _allowed_argv0_set(pins: dict) -> set[str]:
    allowed: set[str] = set()
    for arm in pins.get("arms", {}).values():
        vb = arm.get("venv_bin")
        if vb:
            allowed.add(vb)
        # Rule 1 fix (found live, 160-11 BRINGUP-wrv bring-up -- this record's first-ever
        # real gate_record.py --cell run): capture_provenance.py legitimately invokes each
        # arm's own pinned venv_python directly (the git-HEAD/porcelain probe delegation,
        # the __file__ probe, and the bare `--version` interpreter probe) -- a second,
        # equally-pinned executable per arm, distinct from venv_bin but never added to
        # this allow-list before. Every real command this rig's own tooling produces using
        # it was therefore rejected as an unrecognized binary, unconditionally.
        vp = arm.get("venv_python")
        if vp:
            allowed.add(vp)
    av = pins.get("avrdude", {}).get("binary")
    if av:
        allowed.add(av)
    pio = pins.get("pio_binary")
    if pio:
        allowed.add(pio)
    # Rule 2 fix (found live, 160-08): PROCEDURE.md P-04's own literal command block
    # requires recording `git -C <pio_project_dir> checkout <fw_sha>` in every cell's
    # `commands` field (the firmware-arm checkout), but this set had no allowance for
    # `git` at all -- every future EVIDENCE.jsonl row that followed P-04 literally would
    # have failed this check. Pinned from rig-pins.json's `git_binary`, never PATH.
    git = pins.get("git_binary")
    if git:
        allowed.add(git)
    return allowed


def _is_rig_tool_invocation(argv: list) -> bool:
    """True when argv[0] is an absolute-path interpreter invoking a script that lives
    under .planning/milestones/v1.34-artifacts/tools/ -- the "system interpreter" exception rig-owned tools
    are permitted to record."""
    if len(argv) < 2:
        return False
    token0, script = argv[0], argv[1]
    if not (isinstance(token0, str) and os.path.isabs(token0)):
        return False
    return isinstance(script, str) and os.path.isabs(script) and "/.planning/milestones/v1.34-artifacts/tools/" in script


def check_commands(record: dict, pins: dict) -> list[str]:
    violations: list[str] = []
    commands = record.get("commands")
    if commands is None:
        return violations
    if not isinstance(commands, list):
        return [f"'commands' must be a list, got {type(commands).__name__}"]

    allowed_argv0 = _allowed_argv0_set(pins)
    forbidden_flags = set(pins.get("forbidden_flags", []))
    pio_binary = pins.get("pio_binary")
    pio_project_dir = pins.get("pio_project_dir")
    # Rule 1 fix (found live, 160-09): rig-pins.json's forbidden_flags carries "-b" for
    # firestarter_app's own --no-blank-check flag (Phase 145 D-17's withdrawn permission),
    # but "-b" is ALSO avrdude's own, wholly unrelated baud-rate option (every avrdude
    # invocation this rig makes passes "-b <baud>" -- see judge_readback.py's
    # run_avrdude_read() and probe_board.py's run_avrdude()/run_urclock_probes()). A blind
    # token match against a directly-recorded avrdude command (e.g. the uno328pb bring-up's
    # corroborating "-c arduino" open-attempt, EVIDENCE.jsonl BRINGUP-uno328pb row) would
    # reject a perfectly legitimate avrdude baud argument as though it were the withdrawn
    # app flag. Scoped to the avrdude binary specifically -- the one binary this rig's own
    # avrdude_binary pin resolves to -- not a blanket exemption.
    avrdude_binary = pins.get("avrdude", {}).get("binary")

    def _forbidden_flags_for(token0: object) -> set:
        if avrdude_binary and token0 == avrdude_binary:
            return forbidden_flags - {"-b"}
        return forbidden_flags

    for i, entry in enumerate(commands):
        argv = entry.get("argv") if isinstance(entry, dict) else entry
        cwd = entry.get("cwd") if isinstance(entry, dict) else None
        if not isinstance(argv, list) or not argv:
            violations.append(f"commands[{i}]: not a non-empty argv list")
            continue

        token0 = argv[0]
        if not (isinstance(token0, str) and os.path.isabs(token0)):
            violations.append(
                f"commands[{i}]: first token {token0!r} is not an absolute path -- a bare "
                "invocation would resolve to the un-named user-site editable install"
            )
        elif token0 not in allowed_argv0 and not _is_rig_tool_invocation(argv):
            violations.append(
                f"commands[{i}]: first token {token0!r} is not one of the two pinned arm "
                "binaries or a pinned rig-owned executable"
            )

        bad_flags = _forbidden_flags_for(token0) & set(str(a) for a in argv)
        if bad_flags:
            violations.append(
                f"commands[{i}]: forbidden flag(s) {sorted(bad_flags)} present -- "
                "Phase 145 D-17's withdrawn permission is enforced mechanically here"
            )

        if pio_binary and token0 == pio_binary and cwd is not None and cwd != pio_project_dir:
            violations.append(
                f"commands[{i}]: pio invoked with cwd {cwd!r}, expected {pio_project_dir!r} "
                "-- the same command string succeeds or fails depending on cwd (Pitfall 4)"
            )

    return violations


# ---------------------------------------------------------------------------
# Outcome domain (D-18)
# ---------------------------------------------------------------------------


def check_outcome(record: dict, schema: dict | None) -> list[str]:
    if "outcome" not in record:
        return []
    outcome_values = schema.get("outcome_values") if isinstance(schema, dict) else None
    if not outcome_values:
        return ["record carries 'outcome' but the schema has no outcome_values domain to check it against"]
    if record["outcome"] not in outcome_values:
        return [
            f"outcome {record['outcome']!r} is outside the two-state domain "
            f"{sorted(outcome_values)} -- a third state belongs only to Phase 165's triage "
            "classification of a failure after the fact, never to a cell result"
        ]
    return []


# ---------------------------------------------------------------------------
# Cross-oracle consistency
# ---------------------------------------------------------------------------


def check_cross_oracle(record: dict) -> list[str]:
    violations: list[str] = []
    written = record.get("written_image_sha256")
    read = record.get("read_sha256")
    outcome = str(record.get("outcome", "")).lower()
    if written and read and written != read and outcome == "validated":
        violations.append(
            f"outcome is 'validated' but written_image_sha256 {written!r} != "
            f"read_sha256 {read!r} -- a disagreement between the two SHAs is itself the result"
        )

    judged_matches_written = None
    if written is not None and read is not None:
        judged_matches_written = written == read
    app_verdict = record.get("app_dev_consistency_verdict")
    if app_verdict is not None and judged_matches_written is not None:
        app_says_ok = str(app_verdict) in ("0", "PASS")
        if app_says_ok != judged_matches_written:
            violations.append(
                f"judged SHA verdict ({judged_matches_written}) and the app's own dev "
                f"consistency-check verdict ({app_verdict!r}) disagree -- a disagreement "
                "between two oracles is itself the result, not something to resolve"
            )
    return violations


# ---------------------------------------------------------------------------
# Config-dir integrity (D-07)
# ---------------------------------------------------------------------------


def check_config_dir_sha(record: dict, pins: dict) -> list[str]:
    recorded = record.get("config_dir_sha")
    if not recorded:
        return []
    config_dir = pins.get("config_dir")
    if not config_dir:
        return ["record carries config_dir_sha but rig-pins.json has no config_dir to recompute against"]
    if not Path(config_dir).is_dir():
        return [f"config_dir {config_dir!r} does not exist -- cannot recompute for comparison"]
    ca_mod = _load_check_arms()
    try:
        actual = ca_mod.compute_config_dir_sha(config_dir)
    except OSError as exc:
        return [f"could not recompute config dir sha: {exc}"]
    if actual != recorded:
        return [
            f"config dir sha {actual} != recorded {recorded} -- a config write by one of "
            "the arms (D-07), now a visible recorded event rather than invisible drift"
        ]
    return []


# ---------------------------------------------------------------------------
# Schema extraction + per-object validation
# ---------------------------------------------------------------------------


def load_schema_and_record(obj: dict) -> tuple[dict | None, dict, list[str]]:
    violations: list[str] = []
    schema = obj.get("_schema")
    if not isinstance(schema, dict):
        violations.append("missing or malformed '_schema' block (record_keys + outcome_values)")
        schema = None
    else:
        if not isinstance(schema.get("record_keys"), list):
            violations.append("_schema is missing a 'record_keys' list")
        if not isinstance(schema.get("outcome_values"), list):
            violations.append("_schema is missing an 'outcome_values' list")
    record = {k: v for k, v in obj.items() if k != "_schema"}
    return schema, record, violations


def validate_object(obj: dict, pins: dict) -> list[str]:
    violations: list[str] = []
    schema, record, schema_violations = load_schema_and_record(obj)
    violations.extend(schema_violations)
    required_keys = schema.get("record_keys", []) if isinstance(schema, dict) else []
    violations.extend(check_required_fields(record, required_keys))
    violations.extend(check_commands(record, pins))
    violations.extend(check_outcome(record, schema))
    violations.extend(check_cross_oracle(record))
    violations.extend(check_config_dir_sha(record, pins))
    return violations


def validate_cell_file(path: Path, pins: dict) -> list[str]:
    if not path.exists():
        return [f"input file {path} does not exist"]
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return [f"input file {path} is empty"]
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"input file {path} is not valid JSON: {exc}"]
    if not isinstance(obj, dict):
        return [f"input file {path} does not contain a JSON object at the top level"]
    return validate_object(obj, pins)


def validate_jsonl_file(path: Path, pins: dict) -> list[str]:
    if not path.exists():
        return [f"input file {path} does not exist"]
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return [f"input file {path} is empty"]

    violations: list[str] = []
    schema: dict | None = None
    seen_schema = False

    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            violations.append(f"line {lineno}: blank line in a JSONL file")
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            violations.append(f"line {lineno}: not valid JSON: {exc}")
            continue
        if not isinstance(obj, dict):
            violations.append(f"line {lineno}: not a JSON object")
            continue

        if lineno == 1:
            if "_schema" not in obj:
                violations.append("line 1: missing the '_schema' header record")
            else:
                schema = obj["_schema"]
                seen_schema = True
                if not isinstance(schema.get("record_keys"), list):
                    violations.append("line 1: _schema is missing a 'record_keys' list")
                if not isinstance(schema.get("outcome_values"), list):
                    violations.append("line 1: _schema is missing an 'outcome_values' list")
            continue

        if "_schema" in obj:
            violations.append(f"line {lineno}: '_schema' key must appear only on line 1")
        if not seen_schema:
            violations.append(f"line {lineno}: no valid schema header on line 1 to validate against")
            continue

        required_keys = schema.get("record_keys", []) if isinstance(schema, dict) else []
        row_violations = (
            check_required_fields(obj, required_keys)
            + check_commands(obj, pins)
            + check_outcome(obj, schema)
            + check_cross_oracle(obj)
            + check_config_dir_sha(obj, pins)
        )
        violations.extend(f"line {lineno}: {v}" for v in row_violations)

    return violations


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", help="path to one provenance/cell-record JSON file")
    ap.add_argument("--jsonl", help="path to a whole EVIDENCE.jsonl file")
    ap.add_argument("--pins", default=str(_DEFAULT_PINS), help="path to rig-pins.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    if not args.cell and not args.jsonl:
        print("FAIL: one of --cell or --jsonl is required", file=sys.stderr)
        return 2

    try:
        pins = json.loads(Path(args.pins).read_text())
    except OSError as exc:
        print(f"FAIL: could not read pins file {args.pins}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: pins file {args.pins} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    violations: list[str] = []
    if args.cell:
        violations.extend(validate_cell_file(Path(args.cell), pins))
    if args.jsonl:
        violations.extend(validate_jsonl_file(Path(args.jsonl), pins))

    if violations:
        for v in violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1

    scope = " ".join(
        p for p in (f"--cell {args.cell}" if args.cell else "", f"--jsonl {args.jsonl}" if args.jsonl else "") if p
    )
    print(f"PASS: gate_record validated {scope} with 0 violations")
    return 0


# ---------------------------------------------------------------------------
# --selftest: on-disk fixtures in a temp dir. Positive legs + twelve negative
# legs, each named.
# ---------------------------------------------------------------------------


def _run_selftest() -> int:
    import hashlib
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

    pins = {
        "arms": {
            "control": {
                "venv_bin": "/fake/arms/control/.venv/bin/firestarter",
                "venv_python": "/fake/arms/control/.venv/bin/python",
            },
            "v133": {
                "venv_bin": "/fake/arms/v133/.venv/bin/firestarter",
                "venv_python": "/fake/arms/v133/.venv/bin/python",
            },
        },
        "avrdude": {"binary": "/fake/avrdude", "conf": "/fake/avrdude.conf"},
        "pio_binary": "/fake/pio",
        "pio_project_dir": "/fake/firestarter",
        "git_binary": "/fake/git",
        "forbidden_flags": ["--force", "-f", "-b", "--no-blank-check", "--skip-erase"],
        "config_dir": None,
    }
    arm_bin = pins["arms"]["control"]["venv_bin"]
    sha_a = hashlib.sha256(b"a").hexdigest()
    sha_b = hashlib.sha256(b"b").hexdigest()

    good_schema = {
        "record_keys": ["cell_id", "outcome", "commands", "written_image_sha256", "read_sha256", "note"],
        "outcome_values": ["validated", "skipped-with-reason"],
    }

    def good_record(**overrides) -> dict:
        rec = {
            "_schema": good_schema,
            "cell_id": "A3/B2",
            "outcome": "validated",
            "commands": [{"argv": [arm_bin, "write", "w27c512", "/tmp/x.bin"], "cwd": "/tmp"}],
            "written_image_sha256": sha_a,
            "read_sha256": sha_a,
            "note": "not measured — fixture only, no board attached",
        }
        rec.update(overrides)
        return rec

    tmp = Path(tempfile.mkdtemp(prefix="gate_record_selftest_"))
    try:
        # --- positive: complete self-consistent record ---
        p = tmp / "good.json"
        p.write_text(json.dumps(good_record()), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("positive: complete self-consistent record passes", not v, "; ".join(v))

        # --- positive: a git checkout command (PROCEDURE.md P-04's own recorded
        # invocation) is allowed by argv0, not rejected as an unrecognized binary ---
        git_record = good_record(
            commands=[
                {"argv": [pins["git_binary"], "-C", "/fake/firestarter", "checkout", "deadbeef"], "cwd": "/fake"},
                {"argv": [arm_bin, "write", "w27c512", "/tmp/x.bin"], "cwd": "/tmp"},
            ]
        )
        p = tmp / "git_ok.json"
        p.write_text(json.dumps(git_record), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("positive: a pinned git_binary checkout command is allowed by argv0", not v, "; ".join(v))

        # --- positive: a pinned arm venv_python command (capture_provenance.py's
        # __file__/--version/git-delegation probes) is allowed by argv0, not rejected
        # (Rule 1 fix, 160-11 BRINGUP-wrv: venv_python was missing from the allow-list
        # entirely, distinct from venv_bin) ---
        venv_python = pins["arms"]["v133"]["venv_python"]
        venv_python_record = good_record(
            commands=[
                {"argv": [venv_python, "-P", "-c", "import firestarter; print(firestarter.__file__)"], "cwd": "/fake"},
                {"argv": [venv_python, "--version"], "cwd": "/fake"},
                {"argv": [arm_bin, "write", "w27c512", "/tmp/x.bin"], "cwd": "/tmp"},
            ]
        )
        p = tmp / "venv_python_ok.json"
        p.write_text(json.dumps(venv_python_record), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("positive: a pinned arm venv_python command is allowed by argv0", not v, "; ".join(v))

        # --- positive: two-row jsonl with a valid header ---
        header = {"_schema": good_schema}
        row1 = good_record()
        row1.pop("_schema")
        row2 = good_record(cell_id="A3/B3")
        row2.pop("_schema")
        p = tmp / "good.jsonl"
        p.write_text("\n".join(json.dumps(x) for x in (header, row1, row2)) + "\n", encoding="utf-8")
        v = validate_jsonl_file(p, pins)
        report("positive: two-row jsonl with a valid header passes", not v, "; ".join(v))

        # --- negative 1: null required field ---
        bad = good_record()
        bad["cell_id"] = None
        p = tmp / "neg1.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 1: null required field is caught", bool(v), "; ".join(v))

        # --- negative 2: placeholder value left in place ---
        bad = good_record()
        bad["cell_id"] = "TBD"
        p = tmp / "neg2.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 2: placeholder value is caught", bool(v), "; ".join(v))

        # --- negative 3: blank where 'not measured — reason' was required ---
        bad = good_record()
        bad["note"] = "not measured"
        p = tmp / "neg3.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 3: bare 'not measured' with no reason is caught", bool(v), "; ".join(v))

        # --- negative 4: commands entry whose first token is a bare name ---
        bad = good_record()
        bad["commands"] = [{"argv": ["firestarter", "write"], "cwd": "/tmp"}]
        p = tmp / "neg4.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 4: bare first-token command is caught", bool(v), "; ".join(v))

        # --- negative 5: commands entry carrying a forbidden flag ---
        bad = good_record()
        bad["commands"] = [{"argv": [arm_bin, "write", "--force"], "cwd": "/tmp"}]
        p = tmp / "neg5.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 5: forbidden flag is caught", bool(v), "; ".join(v))

        # --- positive: avrdude's own "-b <baud>" is NOT the withdrawn app flag (160-09
        # Rule 1 fix) -- a directly-recorded avrdude command carrying "-b 115200" must pass ---
        avrdude_ok = good_record(
            commands=[{"argv": [pins["avrdude"]["binary"], "-c", "arduino", "-p", "atmega328pb",
                                 "-b", "115200", "-P", "/dev/ttyUSB0", "-n"], "cwd": "/tmp"}]
        )
        p = tmp / "avrdude_baud_ok.json"
        p.write_text(json.dumps(avrdude_ok), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("positive: avrdude's own -b <baud> argument is not the withdrawn app flag", not v, "; ".join(v))

        # --- negative: "-b" on a NON-avrdude binary (e.g. the arm's own write command) is
        # still caught -- the exemption above must be scoped to the avrdude binary only ---
        bad_arm_b = good_record(commands=[{"argv": [arm_bin, "write", "w27c512", "-b"], "cwd": "/tmp"}])
        p = tmp / "neg5b.json"
        p.write_text(json.dumps(bad_arm_b), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 5b: -b on a non-avrdude binary is still caught (exemption is scoped)", bool(v), "; ".join(v))

        # --- negative 6: pio command recorded with the wrong working directory ---
        bad = good_record()
        bad["commands"] = [{"argv": [pins["pio_binary"], "run", "-e", "uno"], "cwd": "/wrong/dir"}]
        p = tmp / "neg6.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 6: pio wrong-cwd is caught", bool(v), "; ".join(v))

        # --- negative 7: outcome value outside the two-state domain ---
        bad = good_record()
        bad["outcome"] = "inconclusive"
        p = tmp / "neg7.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 7: out-of-domain outcome is caught", bool(v), "; ".join(v))

        # --- negative 8: judged and unjudged verdicts contradict ---
        bad = good_record()
        bad["read_sha256"] = sha_b
        p = tmp / "neg8.json"
        p.write_text(json.dumps(bad), encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 8: written/read SHA contradiction under a validated outcome is caught", bool(v), "; ".join(v))

        # --- negative 9: jsonl line 1 lacks the header ---
        row = good_record()
        row.pop("_schema")
        p = tmp / "neg9.jsonl"
        p.write_text(json.dumps(row) + "\n", encoding="utf-8")
        v = validate_jsonl_file(p, pins)
        report("negative 9: jsonl missing line-1 header is caught", bool(v), "; ".join(v))

        # --- negative 10: jsonl with a blank line ---
        row = good_record()
        row.pop("_schema")
        p = tmp / "neg10.jsonl"
        p.write_text(json.dumps(header) + "\n\n" + json.dumps(row) + "\n", encoding="utf-8")
        v = validate_jsonl_file(p, pins)
        report("negative 10: jsonl blank line is caught", bool(v), "; ".join(v))

        # --- negative 11: jsonl row missing a declared key ---
        row = good_record()
        row.pop("_schema")
        row.pop("note")
        p = tmp / "neg11.jsonl"
        p.write_text(json.dumps(header) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
        v = validate_jsonl_file(p, pins)
        report("negative 11: jsonl row missing a declared key is caught", bool(v), "; ".join(v))

        # --- negative 12: empty or missing input file ---
        v = validate_cell_file(tmp / "does-not-exist.json", pins)
        report("negative 12a: missing input file is caught", bool(v), "; ".join(v))
        p = tmp / "empty.json"
        p.write_text("", encoding="utf-8")
        v = validate_cell_file(p, pins)
        report("negative 12b: empty input file is caught", bool(v), "; ".join(v))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
